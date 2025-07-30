import argparse
import sys
from .config import get_model, set_model
from .agent import get_command_from_llm
from .safety import assess_risk
from .history import save_history, load_history


def cli():
    parser = argparse.ArgumentParser(description="aish: Natural language shell commands via Ollama")
    subparsers = parser.add_subparsers(dest="command")

    use_parser = subparsers.add_parser("use", help="Set Ollama model")
    use_parser.add_argument("model", help="Model name (e.g., llama3)")

    hist_parser = subparsers.add_parser("history", help="Show command history")

    parser.add_argument("query", nargs=argparse.REMAINDER, help="Natural language command")
    args = parser.parse_args()

    if args.command == "use":
        set_model(args.model)
        print(f"[aish] Model set to: {args.model}")
        return
    elif args.command == "history":
        for i, entry in enumerate(load_history(), 1):
            print(f"{i}. {entry['query']}\n   → {entry['command']}\n   [{entry['risk']}]\n")
        return
    elif args.query:
        query = " ".join(args.query)
        model = get_model()
        if not model:
            print("[aish] No model set. Run: aish use model llama3")
            sys.exit(1)
        command = get_command_from_llm(query, model)
        risk = assess_risk(command)
        print(f"\n→ {command}\n[risk: {risk}]\n")
        if risk in ("dangerous", "critical"):
            confirm = input("[aish] This command is risky. Run it? (y/N): ").strip().lower()
            if confirm != "y":
                print("[aish] Cancelled.")
                return
        elif risk == "medium":
            confirm = input("[aish] Run this command? (y/N): ").strip().lower()
            if confirm != "y":
                print("[aish] Cancelled.")
                return
        save_history(query, command, risk)
        import subprocess
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[aish] Command failed: {e}")
    else:
        parser.print_help()

def main():
    cli()

if __name__ == "__main__":
    main() 