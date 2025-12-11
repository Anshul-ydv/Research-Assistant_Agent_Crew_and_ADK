"""
Output Formatters for Structured Output Generation
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class OutputFormatter:
    """Generates structured outputs in multiple formats."""

    def __init__(self, settings):
        self.output_dir = Path(settings.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def _write_file(self, filename: str, content: str) -> str:
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(filepath)

    async def generate_json(self, data: Dict[str, Any]) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content = json.dumps(data, indent=2, default=str)
        return await self._write_file(f"review_{timestamp}.json", content)

    async def generate_markdown(self, data: Dict[str, Any]) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        review_html = data.get("literature_review", "<p>No review generated.</p>")

        # Very small HTML -> markdown conversion for our generated review_html
        markdown = review_html.replace("<h1>", "# ").replace("</h1>", "\n\n")
        markdown = markdown.replace("<h2>", "## ").replace("</h2>", "\n\n")
        markdown = markdown.replace("<p>", "").replace("</p>", "\n\n")

        # Include citations if available in the data package (ReferenceManagerAgent result)
        ref_data = data.get("ReferenceManagerAgent") or {}
        apa_list = ref_data.get("apa", []) if isinstance(ref_data, dict) else []

        if apa_list:
            markdown += "\n## References\n\n"
            for i, cite in enumerate(apa_list, start=1):
                markdown += f"{i}. {cite}\n\n"

        # Add metadata header
        header = f"# Literature Review\nGenerated: {datetime.now().isoformat()}\n\n"
        content = header + markdown
        return await self._write_file(f"review_{timestamp}.md", content)

    async def generate_html(self, data: Dict[str, Any]) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_content = data.get("literature_review", "<p>No review generated.</p>")
        html_head = (
            '<!DOCTYPE html>'
            '<html><head><title>Literature Review</title>'
            '<style>body{font-family:sans-serif;max-width:900px;margin:auto;padding:20px;line-height:1.5} '
            'table{border-collapse:collapse;width:100%} table,th,td{border:1px solid #ddd;padding:8px} th{background:#f4f4f4}'
            '</style></head><body>'
        )
        html = html_head + html_content + '</body></html>'
        return await self._write_file(f"review_{timestamp}.html", html)
