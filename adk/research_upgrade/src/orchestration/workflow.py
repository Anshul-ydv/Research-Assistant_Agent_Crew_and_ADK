"""
Complete Workflow Orchestration
"""
import asyncio
import time
from typing import Dict, Any, List

from src.agents.research_agents import ResearchPlannerAgent, PaperRetrieverAgent, ContentExtractorAgent
from src.agents.analysis_agents import AnalysisAgent, CriticAgent, ValidatorAgent, ReferenceManagerAgent, SynthesisAgent
from src.tools.arxiv_tool import ArXivTool
from src.tools.semantic_scholar_tool import SemanticScholarTool
from src.tools.citation_generator import CitationGeneratorTool
from src.tools.fact_checker_tool import FactCheckerTool
from src.memory.research_memory import ResearchMemory
from src.output.formatters import OutputFormatter

class ResearchWorkflow:
    """Main workflow orchestrator."""
    
    def __init__(self, settings, logger):
        self.settings = settings
        self.logger = logger
        self.memory = ResearchMemory()
        
        # Initialize tools
        self.arxiv_tool = ArXivTool(max_results=settings.arxiv_max_results)
        self.semantic_scholar_tool = SemanticScholarTool(
            api_key=settings.semantic_scholar_api_key,
            max_results=settings.semantic_scholar_max_results
        )
        self.citation_tool = CitationGeneratorTool()
        self.fact_checker = FactCheckerTool()
        
        # Initialize agents
        self.research_planner = ResearchPlannerAgent(self.memory, self.logger)
        self.paper_retriever = PaperRetrieverAgent(self.memory, self.logger, self.arxiv_tool, self.semantic_scholar_tool)
        self.content_extractor = ContentExtractorAgent(self.memory, self.logger)
        self.analysis_agent = AnalysisAgent(self.memory, self.logger)
        self.critic_agent = CriticAgent(self.memory, self.logger)
        self.validator_agent = ValidatorAgent(self.memory, self.logger, self.fact_checker)
        self.reference_manager = ReferenceManagerAgent(self.memory, self.logger, self.citation_tool)
        self.synthesis_agent = SynthesisAgent(self.memory, self.logger)
        
        self.output_formatter = OutputFormatter(settings)
    
    async def execute(self, research_topic: str) -> Dict[str, Any]:
        start_time = time.time()
        self.logger.info(f"WORKFLOW START: {research_topic}")
        try:
            # Sequential Phases
            await self.research_planner.execute(topic=research_topic)
            await self.paper_retriever.execute(max_papers=self.settings.max_papers)
            await self.content_extractor.execute()
            
            # Parallel Phase
            if self.settings.enable_parallel:
                self.logger.info("PARALLEL EXECUTION START: Analysis, Critique, References")
                await asyncio.gather(
                    self.analysis_agent.execute(),
                    self.critic_agent.execute(),
                    self.reference_manager.execute()
                )
            else:
                await self.analysis_agent.execute()
                await self.critic_agent.execute()
                await self.reference_manager.execute()

            # Validation and Synthesis
            if self.settings.enable_validation:
                await self.validator_agent.execute()
            
            synthesis = await self.synthesis_agent.execute()
            
            output_files = await self._generate_outputs(synthesis)

            execution_time = time.time() - start_time
            final_results = {
                "status": "success",
                "execution_time": execution_time,
                "output_files": output_files,
                "papers_analyzed": (self.memory.get_agent_result("ContentExtractorAgent") or {}).get("total_papers", 0),
                "quality_score": (self.memory.get_agent_result("ValidatorAgent") or {}).get("quality_score", "N/A"),
            }
            self.logger.info(f"WORKFLOW COMPLETED in {execution_time:.2f}s")
            return final_results
            
        except Exception as e:
            self.logger.error(f"WORKFLOW FAILED: {str(e)}", exc_info=True)
            raise

    async def _generate_outputs(self, synthesis: Dict) -> List[str]:
        output_files = []
        data_package = {
            "literature_review": synthesis.get("literature_review", ""),
            **self.memory.get_all_results()
        }
        for fmt in self.settings.output_formats:
            try:
                if fmt == "json":
                    fp = await self.output_formatter.generate_json(data_package)
                    output_files.append(fp)
                elif fmt == "markdown":
                    fp = await self.output_formatter.generate_markdown(data_package)
                    output_files.append(fp)
                elif fmt == "html":
                    fp = await self.output_formatter.generate_html(data_package)
                    output_files.append(fp)
            except Exception as e:
                self.logger.error(f"Failed to generate '{fmt}' output: {e}")
        return output_files