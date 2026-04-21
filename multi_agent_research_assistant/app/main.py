from __future__ import annotations

import argparse
import logging

from dotenv import load_dotenv

from app.config import load_config
from app.graph import build_graph
from app.state import make_initial_state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the multi-agent research assistant.")
    parser.add_argument("question", nargs="*", help="Research question to answer.")
    parser.add_argument(
        "--image",
        action="append",
        default=[],
        help="Optional image path to include in the multimodal workflow. Repeat for multiple images.",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = parse_args()

    question = " ".join(args.question).strip()
    if not question:
        question = input("Research question: ").strip()
    if not question:
        raise SystemExit("A research question is required.")

    config = load_config()
    graph = build_graph(config)
    result = graph.invoke(make_initial_state(question, image_paths=args.image))

    print()
    print(result.get("final_answer", "No final report was generated."))


if __name__ == "__main__":
    main()
