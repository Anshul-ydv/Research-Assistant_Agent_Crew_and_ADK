"""
External Tool: ArXiv API (lazy import and graceful degradation)

This module defers importing the external `arxiv` package so the project can be
imported even if `feedparser`/`arxiv` aren't available in the environment
(common for Python 3.13 where some stdlib modules were removed). When the
dependency is missing the tool returns an empty list and logs a warning.
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ArXivTool:
    """Tool for searching ArXiv research papers with graceful fallback."""

    def __init__(self, max_results: int = 100):
        self.max_results = max_results
        self._available = False
        self._client = None
        # Do NOT attempt to import the `arxiv` package at module import time.
        # Some environments (e.g., Python 3.13) remove stdlib modules used by
        # `feedparser` and others, causing import-time failures. We will attempt
        # to import `arxiv` only when a search is requested and otherwise use
        # the HTTP fallback implementation.
        self._arxiv = None

    async def search(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        max_results = max_results or self.max_results
        # On first search attempt, try to import the `arxiv` client. If the
        # import fails (environment incompatibility or missing package), fall
        # back to the HTTP API.
        if not self._available and self._arxiv is None:
            try:
                import arxiv as _arxiv
                self._arxiv = _arxiv
                self._client = _arxiv.Client()
                self._available = True
            except Exception as e:
                # Import failed; use HTTP fallback for this and subsequent calls.
                # Log a concise debug message when the fallback is activated so
                # normal INFO logs stay clean for users who don't want to see
                # this compatibility detail.
                logger.debug(f"ArXiv library import failed; using HTTP fallback ({e})")
                self._available = False

        if not self._available:
            # Fallback: use the public arXiv HTTP API (export.arxiv.org) to fetch results
            try:
                return await self._http_fallback_search(query, max_results)
            except Exception as e:
                logger.debug(f"ArXiv fallback search failed: {e}")
                return []

        try:
            search = self._arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=self._arxiv.SortCriterion.Relevance
            )
            papers = []
            if self._client is None:
                return []
            for result in self._client.results(search):
                paper = {
                    "title": getattr(result, 'title', None),
                    "authors": [getattr(author, 'name', None) for author in getattr(result, 'authors', [])],
                    "abstract": getattr(result, 'summary', ''),
                    "year": str(getattr(getattr(result, 'published', ''), 'year', '')),
                    "url": getattr(result, 'entry_id', ''),
                    "pdf_url": getattr(result, 'pdf_url', None),
                    "source": "arxiv"
                }
                papers.append(paper)
            return papers
        except Exception as e:
            logger.debug(f"ArXiv search error: {str(e)}")
            return []

    async def _http_fallback_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Query arXiv via the export API and parse XML using the stdlib.

        Example API: http://export.arxiv.org/api/query?search_query=all:quantum+computing&start=0&max_results=5
        """
        import requests
        import xml.etree.ElementTree as ET
        from urllib.parse import quote_plus

        base = "http://export.arxiv.org/api/query"
        q = quote_plus(query)
        url = f"{base}?search_query=all:{q}&start=0&max_results={max_results}"
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        text = resp.text

        # Parse minimal XML to extract entries
        root = ET.fromstring(text)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = []
        for entry in root.findall('atom:entry', ns):
            title_el = entry.find('atom:title', ns)
            summary_el = entry.find('atom:summary', ns)
            published_el = entry.find('atom:published', ns)
            idn = entry.find('atom:id', ns)
            authors = []
            for a in entry.findall('atom:author', ns):
                name_el = a.find('atom:name', ns)
                if name_el is not None and name_el.text:
                    authors.append(name_el.text.strip())
            pdf_url = None
            for link in entry.findall('atom:link', ns):
                href = link.attrib.get('href')
                if (link.attrib.get('title') == 'pdf') or (link.attrib.get('type') == 'application/pdf'):
                    pdf_url = href
            title_text = (title_el.text or '').strip() if title_el is not None else None
            summary_text = (summary_el.text or '').strip() if summary_el is not None else ''
            year_text = (published_el.text or '')[:4] if published_el is not None and published_el.text else ''
            entries.append({
                'title': title_text,
                'authors': authors,
                'abstract': summary_text,
                'year': year_text,
                'url': idn.text if idn is not None and idn.text else '',
                'pdf_url': pdf_url,
                'source': 'arxiv'
            })
        return entries