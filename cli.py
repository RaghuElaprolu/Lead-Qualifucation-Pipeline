import argparse
from .llm import ClaudeQualifier, HeuristicQualifier
from .pipeline import run_pipeline


def main() -> None:
    ap = argparse.ArgumentParser(description="Score leads from a CSV.")
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--llm", action="store_true", help="use Claude for notes (needs ANTHROPIC_API_KEY)")
    args = ap.parse_args()
    q = ClaudeQualifier() if args.llm else HeuristicQualifier()
    rep = run_pipeline(args.input, args.output, q)
    print(f"scored={len(rep.scored)} rejected={len(rep.rejected)} dupes={rep.duplicates_dropped} tiers={rep.tier_counts()}")
    for row, why in rep.rejected:
        print(f"  rejected row {row}: {why}")


if __name__ == "__main__":
    main()
