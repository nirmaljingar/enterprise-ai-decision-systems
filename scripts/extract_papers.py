#!/usr/bin/env python3
"""Extract IEEE EADS PDFs placed in data/papers to JSON/TXT summaries."""

import argparse
import sys
from pathlib import Path

from eads.paper_extraction import extract_papers_from_directory


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract text from EADS PDFs.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/papers"),
        help="Directory containing the IEEE PDF files (default: data/papers)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/papers/extracted"),
        help="Directory to write JSON/TXT outputs (default: data/papers/extracted)",
    )
    args = parser.parse_args()

    if not args.input_dir.exists():
        print(f"Input directory not found: {args.input_dir}", file=sys.stderr)
        return 1

    papers = extract_papers_from_directory(args.input_dir, args.output_dir)
    print(f"Extracted {len(papers)} paper(s) to {args.output_dir}")
    for paper in papers:
        print(f"  - {Path(paper.path).name}: {paper.title or '(no title)'} {paper.doi}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
