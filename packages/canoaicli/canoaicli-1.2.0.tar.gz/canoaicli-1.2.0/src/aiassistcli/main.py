import argparse
from aiassistcli.config import configure, get_command_from_ai, load_api_key, refine_prompt
from .history import handle_history
from .run_prompt import run_prompt
from rich.console import Console
from rich.prompt import Prompt

def main():
    parser = argparse.ArgumentParser(prog="ai", description="AI assistant CLI tool")

    subparsers = parser.add_subparsers(dest="command")
    # ai configure
    subparsers.add_parser("configure", help="Configure your AI API key")

    # ai history
    history_parser = subparsers.add_parser("history", help="Show command history")
    history_parser.add_argument("--search", help="Filter by keyword")
    history_parser.add_argument("--limit", type=int, default=10, help="Number of entries to show")
    history_parser.add_argument("action", nargs="?", choices=["clear"], help="Clear history")

    # ai <prompt>
    ask_parser = subparsers.add_parser("ask", help="Ask AI a question")
    ask_parser.add_argument("prompt", nargs=argparse.REMAINDER, help="Ask a question to the AI")
    ask_parser.add_argument("--refine", action="store_true", help="Refine the prompt before sending")

    args = parser.parse_args()

    if args.command == "configure":
        configure()

    elif args.command == "history":
        handle_history(args)

    elif args.command == "ask":
        prompt = " ".join(args.prompt)
        final_prompt = prompt

        if args.refine:
            refined = refine_prompt(prompt)
            final_prompt = refined

        run_prompt(final_prompt)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
