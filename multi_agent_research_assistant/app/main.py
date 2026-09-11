from __future__ import annotations

import argparse
import logging

from dotenv import load_dotenv

from app.config import load_config
from app.service import get_final_report, run_workflow


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
    result = run_workflow(question=question, image_paths=args.image, config=config)
    final_report = get_final_report(result)

    print()
    print(final_report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
