from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .agent import create_agent_from_environment


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="research-agent",
        description="Plan bounded public-web research and write an evidence-first, citation-audited brief.",
    )
    parser.add_argument("question", nargs="+", help="Research question")
    parser.add_argument("--max-results", type=int, default=6, help="Search results per query, capped at 12")
    parser.add_argument("--max-pages", type=int, default=4, help="Pages to fetch, capped at 8")
    parser.add_argument("--use-model", action="store_true", help="Opt in to model-assisted query planning (findings remain extractive)")
    parser.add_argument("--model", help="Model name for an OpenAI-compatible chat endpoint")
    parser.add_argument("--json", action="store_true", help="Emit the structured result as JSON")
    parser.add_argument("--out", help="Write the report to this path instead of stdout")
    args = parser.parse_args()

    question = " ".join(args.question)
    try:
        agent = create_agent_from_environment(use_model=args.use_model, model=args.model)
        result = agent.research(
            question,
            max_results=args.max_results,
            max_pages=args.max_pages,
            use_model=args.use_model,
            model=args.model,
        )
        output = json.dumps(result.to_dict(), indent=2, ensure_ascii=False) if args.json else result.to_markdown()
        if args.out:
            destination = Path(args.out)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(output + ("\n" if not output.endswith("\n") else ""), encoding="utf-8")
            print(f"Wrote {destination}")
        else:
            print(output)
        return 0
    except Exception as exc:
        print(f"research-agent: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
