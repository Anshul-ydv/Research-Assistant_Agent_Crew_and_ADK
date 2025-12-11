# src/agents/analysis_agents.py

from typing import Dict, Any, List
from datetime import datetime
from collections import Counter
from .base import Agent  # Import the base class

class AnalysisAgent(Agent):
    """Analyzes research methods, identifies patterns, and extracts trends."""
    def __init__(self, memory, logger):
        super().__init__("AnalysisAgent", "Methodology Comparison Expert", memory, logger)

    async def execute(self) -> Dict[str, Any]:
        """
        Analyzes extracted content to find trends and compare methodologies.
        
        Returns:
            A dictionary containing the analysis results.
        """
        self.logger.agent_start(self.name, "Analyzing research methodologies and trends")
        try:
            content_result = self.memory.get_agent_result("ContentExtractorAgent")
            if not content_result or not content_result.get("extracted_papers"):
                raise ValueError("No extracted content found in memory to analyze.")
            
            papers = content_result.get("extracted_papers", [])
            
            # Perform mock analysis
            all_methodologies = [method for p in papers for method in p.get("methodology", [])]
            method_counts = Counter(all_methodologies)
            
            comparison_table = [{
                "methodology": method,
                "count": count,
                "percentage": (count / len(all_methodologies) * 100) if all_methodologies else 0,
                "avg_relevance": 0.85 # Mock value
            } for method, count in method_counts.items()]

            all_years = [p.get("year") for p in papers if p.get("year")]
            year_counts = Counter(all_years)
            peak_year = year_counts.most_common(1)[0][0] if year_counts else "N/A"

            result = {
                "methodology_comparison": {
                    "comparison_table": sorted(comparison_table, key=lambda x: x['count'], reverse=True),
                    "total_methodologies": len(method_counts),
                    "most_common": method_counts.most_common(1)[0][0] if method_counts else "N/A"
                },
                "trends_analysis": {
                    "yearly_trends": [{"year": y, "paper_count": c} for y, c in sorted(year_counts.items())],
                    "total_years_covered": len(year_counts),
                    "peak_year": peak_year
                },
                "total_papers_analyzed": len(papers)
            }
            
            self.memory.store_agent_result(self.name, result)
            self.logger.agent_complete(self.name, "success", f"Analyzed {len(papers)} papers and identified {len(method_counts)} methodologies.")
            return result
        except Exception as e:
            self.logger.log_error(self.name, str(e))
            return {"error": str(e)}

class CriticAgent(Agent):
    """Identifies limitations, research gaps, and weaknesses in the body of research."""
    def __init__(self, memory, logger):
        super().__init__("CriticAgent", "Academic Quality Assessor", memory, logger)

    async def execute(self) -> Dict[str, Any]:
        """
        Performs a critical evaluation of the collected research content.
        
        Returns:
            A dictionary containing the critique.
        """
        self.logger.agent_start(self.name, "Critiquing research content to find gaps")
        try:
            # Mock critique based on the presence of content
            if not self.memory.get_agent_result("ContentExtractorAgent"):
                 raise ValueError("No content available to critique.")

            result = {
                "methodological_weaknesses": ["Over-reliance on synthetic datasets.", "Lack of longitudinal studies."],
                "research_gaps": ["Exploration of cross-disciplinary applications.", "Need for standardized evaluation metrics."],
                "contradictions": [],
                "recommendations": ["Incorporate real-world data for validation.", "Develop benchmarks for comparing different approaches."]
            }
            
            self.memory.store_agent_result(self.name, result)
            self.logger.agent_complete(self.name, "success", f"Identified {len(result['research_gaps'])} research gaps.")
            return result
        except Exception as e:
            self.logger.log_error(self.name, str(e))
            return {"error": str(e)}

class ValidatorAgent(Agent):
    """Verifies factual accuracy, checks for consistency, and mitigates hallucinations."""
    def __init__(self, memory, logger, fact_checker):
        super().__init__("ValidatorAgent", "Fact Validation Specialist", memory, logger)
        self.fact_checker = fact_checker

    async def execute(self) -> Dict[str, Any]:
        """
        Validates the results from previous agents to ensure quality and accuracy.
        
        Returns:
            A dictionary with validation scores and status.
        """
        self.logger.agent_start(self.name, "Validating results for accuracy and consistency")
        try:
            # Gather results to validate
            analysis = self.memory.get_agent_result("AnalysisAgent") or {}
            critic = self.memory.get_agent_result("CriticAgent") or {}
            retrieval = self.memory.get_agent_result("PaperRetrieverAgent") or {}

            if not analysis and not critic:
                raise ValueError("No analysis or critique results to validate.")

            # Build candidate claims from analysis + critic outputs
            claims = []
            # Example claim from most-common methodology
            most_common = analysis.get("methodology_comparison", {}).get("most_common")
            if most_common:
                claims.append(f"The most common methodology is {most_common}.")

            # Add top critic-identified claims or suspicious statements
            suspicious = critic.get("suspicious_claims", [])
            for s in suspicious:
                # if critic stored a claim dict
                if isinstance(s, dict) and s.get("claim"):
                    claims.append(s.get("claim"))
                elif isinstance(s, str):
                    claims.append(s)

            # If no explicit suspicious claims, include a short set of summary claims
            if not claims:
                claims.append("Key findings reported by analysis should be factual and grounded in the source literature.")

            papers = retrieval.get("papers", []) if isinstance(retrieval, dict) else []

            # Check each claim using the fact checker tool (limit sources for speed)
            verifications = []
            for claim in claims:
                try:
                    check = await self.fact_checker.check_claim(claim, papers[:3])
                    verifications.append(check)
                except Exception as e:
                    # Log but continue
                    self.logger.log_error(self.name, f"Fact check failed for claim '{claim}': {e}")
                    verifications.append({"claim": claim, "verified": False, "confidence": 0.0, "supporting_sources": []})

            # Compute a simple quality metric based on confidences
            confidences = [v.get("confidence", 0.0) for v in verifications if isinstance(v, dict)]
            quality_score = sum(confidences) / len(confidences) if confidences else 0.0

            result = {
                "quality_score": round(quality_score, 4),
                "factual_accuracy": {
                    "verification_count": len([v for v in verifications if v.get("verified")]),
                    "total_checked": len(verifications),
                    "details": verifications
                },
                "consistency_score": round(quality_score * 0.95, 4),
                "validation_passed": quality_score >= 0.7
            }

            self.memory.store_agent_result(self.name, result)
            self.logger.agent_complete(self.name, "success", f"Validation complete. Final Quality Score: {result['quality_score']:.2f}")
            return result
        except Exception as e:
            self.logger.log_error(self.name, str(e))
            return {"error": str(e)}

class ReferenceManagerAgent(Agent):
    """Generates properly formatted citations (e.g., BibTeX, APA) for all retrieved papers."""
    def __init__(self, memory, logger, citation_tool):
        super().__init__("ReferenceManagerAgent", "Citation Management Specialist", memory, logger)
        self.citation_tool = citation_tool

    async def execute(self) -> Dict[str, Any]:
        """
        Generates BibTeX and APA citations for all retrieved papers.
        
        Returns:
            A dictionary containing lists of BibTeX and APA citations.
        """
        self.logger.agent_start(self.name, "Generating references and citations")
        try:
            retrieval_result = self.memory.get_agent_result("PaperRetrieverAgent")
            if not retrieval_result or not retrieval_result.get("papers"):
                raise ValueError("No retrieved papers found in memory to generate references for.")

            papers = retrieval_result.get("papers", [])
            citations = await self.citation_tool.generate_citations_batch(papers)
            
            self.memory.store_agent_result(self.name, citations)
            self.logger.agent_complete(self.name, "success", f"Generated {citations.get('count', 0)} citations in BibTeX and APA formats.")
            return citations
        except Exception as e:
            self.logger.log_error(self.name, str(e))
            return {"error": str(e)}

class SynthesisAgent(Agent):
    """Synthesizes all analyzed results into a comprehensive, publication-ready literature review."""
    def __init__(self, memory, logger):
        super().__init__("SynthesisAgent", "Master Academic Writer", memory, logger)

    async def execute(self) -> Dict[str, Any]:
        """
        Creates the final literature review document by synthesizing all prior results.
        
        Returns:
            A dictionary containing the final HTML literature review and its word count.
        """
        self.logger.agent_start(self.name, "Synthesizing final literature review")
        try:
            topic = self.memory.get_context("research_topic") or "Unspecified Topic"
            analysis = self.memory.get_agent_result("AnalysisAgent") or {}
            critique = self.memory.get_agent_result("CriticAgent") or {}
            content = self.memory.get_agent_result("ContentExtractorAgent") or {}
            references = self.memory.get_agent_result("ReferenceManagerAgent") or {}

            # Build extended sections
            most_common_method = analysis.get("methodology_comparison", {}).get("most_common", "various methods")
            methodology_table = analysis.get("methodology_comparison", {}).get("comparison_table", [])
            trends = analysis.get("trends_analysis", {})
            research_gaps = critique.get("research_gaps", ["Further empirical studies needed."])
            recommendations = critique.get("recommendations", ["Broaden datasets, standardize evaluation."])

            # Per-paper summaries
            extracted = content.get("extracted_papers", [])
            paper_sections = ""
            for idx, p in enumerate(extracted, start=1):
                title = p.get("title", "Untitled")
                authors = ", ".join(p.get("authors", [])) if p.get("authors") else "Unknown"
                year = p.get("year", "n.d.")
                abstract = (p.get("abstract") or "").strip()
                abstract_snip = (abstract[:600] + "...") if len(abstract) > 600 else abstract
                paper_sections += f"<h3>{idx}. {title} ({year})</h3>"
                paper_sections += f"<p><em>Authors:</em> {authors}</p>"
                if abstract_snip:
                    paper_sections += f"<p><strong>Abstract summary:</strong> {abstract_snip}</p>"
                paper_sections += f"<p><a href=\"{p.get('url','')}\">View Paper</a></p>"

            # Methodology comparison table HTML
            table_rows = ""
            for row in methodology_table:
                method = row.get("methodology", "Unknown")
                count = row.get("count", 0)
                pct = f"{row.get('percentage', 0):.1f}%"
                avg_rel = row.get('avg_relevance', 0)
                table_rows += f"<tr><td>{method}</td><td>{count}</td><td>{pct}</td><td>{avg_rel:.2f}</td></tr>"

            references_html = ""
            apa_list = references.get("apa", []) if isinstance(references, dict) else []
            if apa_list:
                references_html += "<h2>References</h2><ol>"
                for cite in apa_list:
                    references_html += f"<li>{cite}</li>"
                references_html += "</ol>"

            # Compose extended review
            review_html = f"""
<h1>Systematic Literature Review: {topic}</h1>
<h2>Executive Summary</h2>
<p>This automated literature review synthesizes findings from {len(extracted)} papers on <strong>{topic}</strong>. It includes per-paper summaries, a detailed methodology comparison, trends across years, identified research gaps, and actionable recommendations.</p>

<h2>Key Findings</h2>
<p>The analysis identified <strong>{most_common_method}</strong> as the most frequently used methodology. Trends and yearly coverage indicate {trends.get('total_years_covered', 'N/A')} years covered with peak activity in {trends.get('peak_year', 'N/A')}.</p>

<h2>Methodology Comparison</h2>
<table border="1" cellpadding="6" cellspacing="0"><thead><tr><th>Methodology</th><th>Count</th><th>Percentage</th><th>Avg Relevance</th></tr></thead><tbody>
{table_rows}
</tbody></table>

<h2>Per-paper Summaries</h2>
{paper_sections}

<h2>Research Gaps</h2>
<ul>
"""
            for gap in research_gaps:
                review_html += f"<li>{gap}</li>"
            review_html += "</ul>\n"

            review_html += "<h2>Recommendations</h2><ol>\n"
            for rec in recommendations:
                review_html += f"<li>{rec}</li>"
            review_html += "</ol>\n"

            review_html += references_html

            # Conclusion and metadata
            review_html += f"<h2>Conclusion</h2><p>This review provides a synthesized snapshot of the state-of-the-art for {topic}. Use the references and per-paper summaries to dive deeper into specific works.</p>"

            result = {"literature_review": review_html, "word_count": len(review_html.split())}
            self.memory.store_agent_result(self.name, result)
            self.logger.agent_complete(self.name, "success", f"Synthesized a {result['word_count']}-word literature review.")
            return result
        except Exception as e:
            self.logger.log_error(self.name, str(e))
            return {"error": str(e)}