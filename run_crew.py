import sys
from src.research_crew.main import run

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.extend(['run', 'machine learning'])
    elif len(sys.argv) == 2:
        topic = sys.argv[1]
        sys.argv = [sys.argv[0], 'run', topic]
    
    result = run()
    sys.exit(0)
