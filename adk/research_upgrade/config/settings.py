"""
Configuration Settings for Google ADK Research Assistant
"""

import os
from dataclasses import dataclass, field
from typing import List
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Settings:
    """Application settings"""

    # API Keys
    google_api_key: str = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    semantic_scholar_api_key: str = field(default_factory=lambda: os.getenv("SEMANTIC_SCHOLAR_API_KEY", ""))

    # Research Parameters
    max_papers: int = 50

    # Agent Configuration
    enable_parallel: bool = True
    enable_validation: bool = True

    # Tool Configuration
    arxiv_max_results: int = 100
    semantic_scholar_max_results: int = 100
    web_scraper_timeout: int = 30

    # Output Configuration
    output_dir: str = "./output"
    output_formats: List[str] = field(default_factory=lambda: ["markdown", "json", "html"])

    # Logging Configuration
    log_level: str = "INFO"
    verbose: bool = False

    # Memory Configuration
    memory_cache_size: int = 1000
    memory_ttl: int = 3600  # 1 hour in seconds

    # Validation Configuration
    fact_check_threshold: float = 0.8
    consistency_threshold: float = 0.75

    def __post_init__(self):
        """Validate and setup settings"""
        # Create output directory
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        (Path(self.output_dir) / "logs").mkdir(exist_ok=True)
        
        if not self.google_api_key:
            print("⚠️  Warning: GOOGLE_API_KEY not set in environment. The application may not function correctly.")

    def to_dict(self) -> dict:
        """Convert settings to a dictionary for logging."""
        return {
            "max_papers": self.max_papers,
            "enable_parallel": self.enable_parallel,
            "enable_validation": self.enable_validation,
            "output_formats": self.output_formats,
            "verbose": self.verbose
        }