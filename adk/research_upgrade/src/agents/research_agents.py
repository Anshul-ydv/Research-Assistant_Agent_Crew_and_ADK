"""
Prompt templates for agents. While this simulation uses Gemini to generate mock data,
these prompts would be used by a real LLM-powered agent system.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import asyncio

from .base import Agent


@dataclass
class AgentPrompts:
    """Prompt templates for agents"""

    RESEARCH_PLANNER = """
    You are an expert Research Planner. Analyze the research topic "{topic}" and create a comprehensive search strategy in JSON format.
    Include: 5-7 key subtopics, 10-15 optimized search queries, key terminology, a recommended time frame, and relevant research domains.
    """

    PAPER_RETRIEVER = """
    You are an Academic Database Navigator. Find the most relevant academic papers based on this strategy: {strategy}.
    Use ArXiv and Semantic Scholar tools to search using the queries. Filter for relevance and quality.
    Return a JSON list of up to {max_papers} papers.
    """

    CONTENT_EXTRACTOR = """
    You are a Research Analyst. Extract and organize key information from these papers: {papers}.
    For each paper, extract: research focus, methodology, key findings from abstracts, and contributions.
    Return a JSON list of structured content.
    """


class ResearchPlannerAgent(Agent):
    """Creates a search strategy for a given research topic."""
    def __init__(self, memory, logger):
        super().__init__("ResearchPlannerAgent", "Research Planning", memory, logger)

    async def execute(self, topic: Optional[str] = None) -> Dict[str, Any]:
        topic = topic or self.memory.get_context("research_topic") or "Unspecified Topic"
        self.logger.agent_start(self.name, f"Planning research for topic: {topic}")
        # Mock strategy
        strategy = {
            "topic": topic,
            "subtopics": [f"{topic} subtopic {i}" for i in range(1, 6)],
            "queries": [f"{topic} research {i}" for i in range(1, 11)]
        }
        self.memory.store_context("research_topic", topic)
        self.memory.store_context("search_strategy", strategy)
        self.memory.store_agent_result(self.name, strategy)
        self.logger.agent_complete(self.name, "success", "Research strategy created.")
        return strategy


class PaperRetrieverAgent(Agent):
    """Retrieves papers using ArXiv and Semantic Scholar tools."""
    def __init__(self, memory, logger, arxiv_tool=None, semantic_tool=None):
        super().__init__("PaperRetrieverAgent", "Paper Retrieval", memory, logger)
        self.arxiv_tool = arxiv_tool
        self.semantic_tool = semantic_tool

    async def execute(self, max_papers: int = 10) -> Dict[str, Any]:
        self.logger.agent_start(self.name, "Retrieving papers from external sources")
        strategy = self.memory.get_context("search_strategy") or {}
        query = strategy.get("queries", [""])[0] if strategy else ""

        papers: List[Dict[str, Any]] = []
        try:
            tasks = []
            if self.arxiv_tool:
                tasks.append(self.arxiv_tool.search(query, max_results=min(max_papers, 10)))
            if self.semantic_tool:
                tasks.append(self.semantic_tool.search(query, max_results=min(max_papers, 10)))

            if tasks:
                results = await asyncio.gather(*tasks)
                for r in results:
                    if isinstance(r, list):
                        papers.extend(r)

            # Deduplicate by title
            seen = set()
            unique_papers = []
            for p in papers:
                title = p.get("title") or p.get("url")
                if title and title not in seen:
                    seen.add(title)
                    unique_papers.append(p)

            unique_papers = unique_papers[:max_papers]
            result = {"papers": unique_papers, "count": len(unique_papers)}
            self.memory.store_agent_result(self.name, result)
            self.logger.agent_complete(self.name, "success", f"Retrieved {len(unique_papers)} papers.")
            return result
        except Exception as e:
            self.logger.log_error(self.name, str(e))
            return {"error": str(e)}


class ContentExtractorAgent(Agent):
    """Extracts structured information from retrieved papers."""
    def __init__(self, memory, logger):
        super().__init__("ContentExtractorAgent", "Content Extraction", memory, logger)

    async def execute(self) -> Dict[str, Any]:
        self.logger.agent_start(self.name, "Extracting content from papers")
        retrieval = self.memory.get_agent_result("PaperRetrieverAgent") or {}
        papers = retrieval.get("papers", []) if retrieval else []

        extracted = []
        for p in papers:
            extracted.append({
                "title": p.get("title"),
                "authors": p.get("authors", []),
                "abstract": p.get("abstract", ""),
                "methodology": ["unspecified"],
                "year": p.get("year", ""),
                "url": p.get("url", p.get("pdf_url"))
            })

        result = {"extracted_papers": extracted, "total_papers": len(extracted)}
        self.memory.store_agent_result(self.name, result)
        self.logger.agent_complete(self.name, "success", f"Extracted content from {len(extracted)} papers.")
        return result
