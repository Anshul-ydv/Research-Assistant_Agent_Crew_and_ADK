
import time
import sys
import time
import json
from pathlib import Path
from src.research_crew.crew import ResearchPaperAnalysisCrew

def save_output(result, research_topic):
    """Save the crew output to both .md and .json files."""
    
    # Create outputs directory if it doesn't exist
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Create safe filename
    safe_topic = "".join(c for c in research_topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_topic = safe_topic.replace(' ', '_')
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    base_filename = f"{safe_topic}_{timestamp}"
    
    # Save as Markdown
    md_file = output_dir / f"{base_filename}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# Research Analysis: {research_topic}\n\n")
        f.write(f"**Generated on:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write("## Results\n\n")
        f.write(str(result))
    
    # Save as JSON
    json_file = output_dir / f"{base_filename}.json"
    output_data = {
        "research_topic": research_topic,
        "generated_on": time.strftime('%Y-%m-%d %H:%M:%S'),
        "result": str(result),
        "raw_result": result.raw if hasattr(result, 'raw') else None,
        "tasks_output": [str(task) for task in result.tasks_output] if hasattr(result, 'tasks_output') else None
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n done done Output saved done done!")
    print(f"Markdown: {md_file}")
    print(f"JSON: {json_file}")

def run():
    """Run the Research Paper Analysis crew with rate limiting."""
    if len(sys.argv) > 2:
        research_topic = sys.argv[2]
    else:
        research_topic = "Solar Energy"

    inputs = {'research_topic': research_topic}

    # Add delay to avoid hitting rate limits
    print(f"🔍 Starting research analysis on: '{research_topic}'")
    print("Starting crew execution with rate limiting...")
    time.sleep(2)  # 2 second delay before starting

    try:
        result = ResearchPaperAnalysisCrew().crew().kickoff(inputs=inputs)  # ← Store result
        save_output(result, research_topic)  # ← Add this line
        return result  # ← Add this line
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            print("Rate limit hit. Waiting 10 seconds before retry...")
            time.sleep(10)
            # Retry once
            result = ResearchPaperAnalysisCrew().crew().kickoff(inputs=inputs)
            save_output(result, research_topic)  # ← Add this line for retry too
            return result
        else:
            raise e
        
def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'research_topic': 'sample_value'
    }
    try:
        # Fix: Use sys.argv[2] and sys.argv[3] since sys.argv[1] is 'train'
        ResearchPaperAnalysisCrew().crew().train(
            n_iterations=int(sys.argv[2]), 
            filename=sys.argv[3], 
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        # Fix: Use sys.argv[2] since sys.argv[1] is 'replay'
        ResearchPaperAnalysisCrew().crew().replay(task_id=sys.argv[2])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'research_topic': 'sample_value'
    }
    try:
        # Fix: Use sys.argv[2] and sys.argv[3] since sys.argv[1] is 'test'
        ResearchPaperAnalysisCrew().crew().test(
            n_iterations=int(sys.argv[2]), 
            eval_llm=sys.argv[3], 
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <command> [<args>]")
        print("Commands:")
        print("  run [research_topic]    - Run the crew")
        print("  train <iterations> <filename> - Train the crew")
        print("  replay <task_id>        - Replay execution")
        print("  test <iterations> <eval_llm> - Test the crew")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run":
        run()
    elif command == "train":
        if len(sys.argv) < 4:
            print("Usage: python main.py train <iterations> <filename>")
            sys.exit(1)
        train()
    elif command == "replay":
        if len(sys.argv) < 3:
            print("Usage: python main.py replay <task_id>")
            sys.exit(1)
        replay()
    elif command == "test":
        if len(sys.argv) < 4:
            print("Usage: python main.py test <iterations> <eval_llm>")
            sys.exit(1)
        test()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: run, train, replay, test")
        sys.exit(1)