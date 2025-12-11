"""
External Tool: Semantic Scholar API
"""
import requests
from typing import List, Dict, Any, Optional
import logging
import time
import random

logger = logging.getLogger(__name__)

class SemanticScholarTool:
    """Tool for searching Semantic Scholar."""
    
    def __init__(self, api_key: Optional[str] = None, max_results: int = 100):
        self.api_key = api_key
        self.max_results = max_results
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.headers = {'x-api-key': api_key} if api_key else {}
    
    async def search(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        max_results = max_results or self.max_results
        fields = ['title', 'abstract', 'year', 'authors', 'url', 'externalIds']

        url = f"{self.base_url}/paper/search"
        params = {'query': query, 'limit': min(max_results, 100), 'fields': ','.join(fields)}

        session = requests.Session()

        max_attempts = 4
        for attempt in range(1, max_attempts + 1):
            try:
                response = session.get(url, params=params, headers=self.headers, timeout=15)

                # If rate-limited, try to respect Retry-After header and backoff
                if response.status_code == 429:
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        try:
                            wait = int(retry_after)
                        except ValueError:
                            # Could be a HTTP-date; fall back to exponential backoff
                            wait = None
                    else:
                        wait = None

                    if wait is None:
                        # exponential backoff with jitter
                        wait = (2 ** attempt) + random.uniform(0, 1)

                    logger.debug(f"Semantic Scholar 429 received; attempt {attempt}/{max_attempts}, sleeping {wait:.1f}s")
                    time.sleep(wait)
                    continue

                response.raise_for_status()
                data = response.json().get('data', [])

                papers = [{
                    'title': item.get('title'),
                    'abstract': item.get('abstract', ''),
                    'year': str(item.get('year', '')),
                    'authors': [author.get('name') for author in item.get('authors', [])],
                    'url': item.get('url', ''),
                    'doi': item.get('externalIds', {}).get('DOI'),
                    'source': 'semantic_scholar'
                } for item in data]
                return papers

            except requests.exceptions.RequestException as e:
                # For HTTP errors other than rate limits, decide whether to retry.
                status = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
                logger.debug(f"Semantic Scholar request failed (attempt {attempt}): {e}")
                if attempt == max_attempts:
                    logger.debug("Semantic Scholar: max retry attempts reached; returning empty list")
                    return []
                # small backoff before retrying
                backoff = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(backoff)

        # If we exit the loop without returning, return empty list
        return []