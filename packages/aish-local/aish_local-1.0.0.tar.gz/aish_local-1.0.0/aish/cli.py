# import argparse
# import sys
# from .config import get_model, set_model
# from .agent import get_command_from_llm
# from .safety import assess_risk
# from .history import save_history, load_history

# def cli():
#     parser = argparse.ArgumentParser(description="aish: Natural language shell commands via Ollama")

#     subparsers = parser.add_subparsers(dest="command", required=True)

#     # aish use llama3
#     use_parser = subparsers.add_parser("use", help="Set Ollama model")
#     use_parser.add_argument("model", help="Model name (e.g., llama3)")

#     # aish history
#     hist_parser = subparsers.add_parser("history", help="Show command history")

#     # aish query "list files"
#     query_parser = subparsers.add_parser("query", help="Ask a natural language command")
#     query_parser.add_argument("nl_query", nargs="+", help="Your natural language query")

#     args = parser.parse_args()

#     if args.command == "use":
#         set_model(args.model)
#         print(f"[aish] Model set to: {args.model}")

#     elif args.command == "history":
#         for i, entry in enumerate(load_history(), 1):
#             print(f"{i}. {entry['query']}\n   → {entry['command']}\n   [{entry['risk']}]\n")

#     elif args.command == "query":
#         query = " ".join(args.nl_query)
#         model = get_model()
#         if not model:
#             print("[aish] No model set. Run: aish use llama3")
#             sys.exit(1)

#         command = get_command_from_llm(query, model)
#         risk = assess_risk(command)

#         print(f"\n→ {command}\n[risk: {risk}]\n")

#         if risk in ("dangerous", "critical"):
#             confirm = input("[aish] This command is risky. Run it? (y/N): ").strip().lower()
#             if confirm != "y":
#                 print("[aish] Cancelled.")
#                 return
#         elif risk == "medium":
#             confirm = input("[aish] Run this command? (y/N): ").strip().lower()
#             if confirm != "y":
#                 print("[aish] Cancelled.")
#                 return

#         save_history(query, command, risk)

#         import subprocess
#         try:
#             subprocess.run(command, shell=True, check=True)
#         except subprocess.CalledProcessError as e:
#             print(f"[aish] Command failed: {e}")


# def main():
#     cli()

# if __name__ == "__main__":
#     main() 



import argparse
import sys
import subprocess

from .config import get_model, set_model
from .agent import get_translator
from .safety import assess_risk
from .history import save_history, load_history

def cli():
    parser = argparse.ArgumentParser(description="aish: Natural language shell commands via Ollama")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Command: aish use llama3
    use_parser = subparsers.add_parser("use", help="Set Ollama model")
    use_parser.add_argument("model", help="Model name (e.g., llama3)")

    # Command: aish history
    hist_parser = subparsers.add_parser("history", help="Show command history")

    # Command: aish query "list files"
    query_parser = subparsers.add_parser("query", help="Ask a natural language command")
    query_parser.add_argument("nl_query", nargs="+", help="Your natural language query")

    args = parser.parse_args()

    if args.command == "use":
        set_model(args.model)
        print(f"[aish] Model set to: {args.model}")

    elif args.command == "history":
        for i, entry in enumerate(load_history(), 1):
            print(f"{i}. {entry['query']}\n   → {entry['command']}\n   [{entry['risk']}]\n")

    elif args.command == "query":
        query = " ".join(args.nl_query)
        model = get_model()
        if not model:
            print("[aish] No model set. Run: aish use llama3")
            sys.exit(1)

        translator = get_translator()
        try:
            result = translator.translate_with_ollama(query)
        except Exception as e:
            print(f"[aish] Failed to translate command: {e}")
            sys.exit(1)

        command = result["command"]
        explanation = result.get("explanation", "No explanation provided")
        risk = assess_risk(command)

        print(f"\n→ {command}\n[risk: {risk}]")
        print(f"[explanation] {explanation}\n")

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

        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[aish] Command failed: {e}")

def main():
    cli()

if __name__ == "__main__":
    main()
