import os
import json
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ArxivPaperTool, ScrapeWebsiteTool  
from crewai_tools import SerplyScholarSearchTool



scholar_search = SerplyScholarSearchTool()

@CrewBase
class ResearchPaperAnalysisCrew:
    """ResearchPaperAnalysis crew"""

    @agent
    def research_planner(self) -> Agent:
        return Agent(
            role="Research Planning Strategist",
            goal="Develop comprehensive research strategies for academic literature analysis on {research_topic} with 3-5 key areas",
            backstory="You are an experienced research strategist with expertise in academic methodology and literature review planning. You excel at breaking down complex research topics into manageable components.",
            tools=[],
            llm=LLM(
                model="gemini/gemini-2.0-flash-lite",
                temperature=0.7,
                max_retries=3,  # Retry failed requests
                timeout=60
            ),
            max_iter=10,
            allow_delegation=False
        )

    @agent
    def paper_retriever(self) -> Agent:
        return Agent(
            role="Academic Paper Retrieval Specialist",
            goal="Find and collect relevant academic papers and research documents for {research_topic}",
            backstory="You are a skilled researcher who knows how to navigate academic databases, ArXiv, and scholarly resources to find the most relevant and high-quality papers.",
            tools=[ArxivPaperTool(), ScrapeWebsiteTool(), SerplyScholarSearchTool()],  # Removed SerplyScholarSearchTool()
            llm=LLM(
                model="gemini/gemini-2.0-flash-lite",
                temperature=0.7,
                max_retries=3,  # Retry failed requests
                timeout=60
            ),
            max_iter=10,
            allow_delegation=False
        )

    @agent
    def content_extractor(self) -> Agent:
        return Agent(
            role="Content Extraction Analyst",
            goal="Extract key information, methodologies, and findings from academic papers",
            backstory="You specialize in reading and extracting crucial information from academic papers, focusing on methodologies, results, and key contributions.",
            tools=[ScrapeWebsiteTool()],
            llm=LLM(
                model="gemini/gemini-2.0-flash-lite",
                temperature=0.7,
                max_retries=3,  # Retry failed requests
                timeout=60
            ),
            max_iter=10,
            allow_delegation=False
        )

    @agent
    def analysis_agent(self) -> Agent:
        return Agent(
            role="Research Analysis Expert",
            goal="Analyze methodologies, results, and contributions from collected research papers",
            backstory="You are an analytical expert who can identify patterns, trends, and insights across multiple research papers, with a focus on methodology evaluation.",
            tools=[],
            llm=LLM(
                model="gemini/gemini-2.0-flash-lite",
                temperature=0.7,
                max_retries=3,  # Retry failed requests
                timeout=60
            ),
            max_iter=10,
            allow_delegation=False
        )

    @agent
    def critic_agent(self) -> Agent:
        return Agent(
            role="Critical Literature Reviewer",
            goal="Provide critical evaluation and identify gaps, limitations, and future research directions",
            backstory="You are a critical thinker with extensive experience in peer review and academic evaluation, skilled at identifying strengths, weaknesses, and research gaps.",
            tools=[],
            llm=LLM(
                model="gemini/gemini-2.0-flash-lite",
                temperature=0.7,
                max_retries=3,  # Retry failed requests
                timeout=60
            ),
            max_iter=10,
            allow_delegation=False
        )

    @agent
    def synthesis_agent(self) -> Agent:
        return Agent(
            role="Literature Review Synthesizer",
            goal="Create comprehensive literature reviews and synthesis reports",
            backstory="You excel at synthesizing complex research findings into coherent, well-structured literature reviews that highlight key themes, trends, and future directions.",
            tools=[],
            llm=LLM(
                model="gemini/gemini-2.0-flash-lite",
                temperature=0.7,
                max_retries=3,  # Retry failed requests
                timeout=60
            ),
            max_iter=10,
            allow_delegation=False
        )

    @task
    def research_strategy_development(self) -> Task:
        return Task(
            description="Create a comprehensive research strategy for analyzing literature on {research_topic}, including key search terms, databases to target, and analysis framework.",
            expected_output="A detailed research strategy document outlining search methodology, key databases, search terms, and analysis framework for {research_topic}.",
            agent=self.research_planner()
        )

    @task
    def academic_paper_collection(self) -> Task:
        return Task(
            description="Search and collect 3-6 relevant academic papers from ArXiv, Google Scholar, and other academic sources related to {research_topic}.",
            expected_output="A collection of 3-6 relevant academic papers with metadata including titles, authors, abstracts, and URLs for {research_topic}.",
            agent=self.paper_retriever(),
            context=[self.research_strategy_development()]
        )

    @task
    def paper_content_extraction(self) -> Task:
        return Task(
            description="Extract key information from the collected papers including methodologies, results, datasets used, and main contributions.",
            expected_output="Structured extraction of key information from each paper including methodology, results, limitations, and contributions.",
            agent=self.content_extractor(),
            context=[self.academic_paper_collection()]
        )

    @task
    def methodology_and_results_analysis(self) -> Task:
        return Task(
            description="Analyze the methodologies and results across papers to identify patterns, trends, and comparative insights.",
            expected_output="Comparative analysis of methodologies and results across papers, highlighting trends, effectiveness, and innovation patterns.",
            agent=self.analysis_agent(),
            context=[self.paper_content_extraction()]
        )

    @task
    def critical_literature_evaluation(self) -> Task:
        return Task(
            description="Provide critical evaluation of the literature, identifying strengths, limitations, gaps, and areas for future research.",
            expected_output="Critical evaluation report highlighting literature strengths, limitations, research gaps, and future research opportunities.",
            agent=self.critic_agent(),
            context=[self.methodology_and_results_analysis()]
        )

    @task
    def comprehensive_literature_review_synthesis(self) -> Task:
        return Task(
            description="Create a comprehensive literature review synthesis that integrates all findings, analyses, and critical evaluations into a cohesive academic document.",
            expected_output="A comprehensive literature review document with introduction, methodology overview, key findings synthesis, critical analysis, and future directions for {research_topic}.",
            agent=self.synthesis_agent(),
            context=[self.critical_literature_evaluation()]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ResearchPaperAnalysis crew"""
        return Crew(
            agents=[
                self.research_planner(),
                self.paper_retriever(),
                self.content_extractor(),
                self.analysis_agent(),
                self.critic_agent(),
                self.synthesis_agent()
            ],
            tasks=[
                self.research_strategy_development(),
                self.academic_paper_collection(),
                self.paper_content_extraction(),
                self.methodology_and_results_analysis(),
                self.critical_literature_evaluation(),
                self.comprehensive_literature_review_synthesis()
            ],
            process=Process.sequential,
            verbose=True,
        )