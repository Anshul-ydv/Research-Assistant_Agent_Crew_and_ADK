"""
Custom Tool: Citation Generator
"""
import re
from typing import Dict, List

class CitationGeneratorTool:
    """Generates academic citations in BibTeX and APA formats."""
    
    def _generate_citation_key(self, authors: List[str], year: str, title: str) -> str:
        if not authors:
            author_part = "unknown"
        else:
            first_author_last_name = authors[0].split()[-1]
            author_part = re.sub(r'[^a-zA-Z]', '', first_author_last_name).lower()
        
        title_first_word = re.sub(r'[^a-zA-Z]', '', title.split()[0]).lower()
        return f"{author_part}{year}{title_first_word}"

    async def generate_bibtex(self, paper: Dict) -> str:
        cite_key = self._generate_citation_key(paper.get('authors', []), paper.get('year', '2024'), paper.get('title', ''))
        authors = ' and '.join(paper.get('authors', []))
        return f"""@article{{{cite_key},
  author = {{{authors}}},
  title = {{{paper.get('title', 'No Title')}}},
  year = {{{paper.get('year', 'N/A')}}}
}}"""

    async def generate_apa(self, paper: Dict) -> str:
        authors = ', '.join(paper.get('authors', []))
        return f"{authors} ({paper.get('year', 'N/A')}). {paper.get('title', 'No Title')}."
    
    async def generate_citations_batch(self, papers: List[Dict]) -> Dict:
        bibtex = [await self.generate_bibtex(p) for p in papers]
        apa = [await self.generate_apa(p) for p in papers]
        return {"bibtex": bibtex, "apa": apa, "count": len(papers)}