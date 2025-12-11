import sys
import os

# Add the project root to Python path so Python can find 'src'
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now Python knows where to find 'src'
from src.research_crew.main import run

if __name__ == "__main__":
    run()