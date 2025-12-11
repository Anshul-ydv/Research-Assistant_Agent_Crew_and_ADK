"""
Main entry point for the Research Assistant
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Ensure `src` package is importable when running this script directly
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
SRC_DIR = PROJECT_ROOT / "src"
# Don't insert the `src` directory itself into sys.path — that breaks
# imports that use the `src.` package namespace. Adding the project root
# (which contains `src/`) is sufficient so `import src...` resolves.

from src.orchestration.workflow import ResearchWorkflow
from config.settings import Settings
from src.monitoring.logger import WorkflowLogger


async def main():
    parser = argparse.ArgumentParser(description="Run the Research Workflow")
    parser.add_argument("topic", nargs="?", default="Artificial Intelligence in Healthcare", help="Research topic to analyze")
    parser.add_argument("--max-papers", type=int, default=10, help="Maximum number of papers to retrieve and analyze")
    parser.add_argument("--output-dir", type=str, default=None, help="Override output directory")
    args = parser.parse_args()

    # Initialize settings and logger
    settings = Settings()
    if args.output_dir:
        settings.output_dir = args.output_dir
    settings.max_papers = args.max_papers
    logger = WorkflowLogger(verbose=settings.verbose)

    try:
        # Initialize the research workflow
        workflow = ResearchWorkflow(settings, logger)

        # Execute the workflow with the provided topic
        print(f"Running research workflow for topic: {args.topic}")
        results = await workflow.execute(args.topic)

        # Print results summary
        print("\nWorkflow Results:")
        print(f"Status: {results['status']}")
        print(f"Execution Time: {results['execution_time']:.2f} seconds")
        print(f"Papers Analyzed: {results['papers_analyzed']}")
        print(f"Quality Score: {results['quality_score']}")
        print("\nOutput Files:")
        for file in results['output_files']:
            print(f"- {file}")

    except Exception as e:
        logger.error(f"Main workflow failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())