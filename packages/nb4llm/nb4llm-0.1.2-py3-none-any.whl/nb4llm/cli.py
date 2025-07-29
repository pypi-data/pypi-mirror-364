#!/usr/bin/env python3
"""
CLI interface for nb4llm - Convert Jupyter notebooks to/from text format for LLM processing.
"""

import argparse
import sys
from pathlib import Path

from .converter import convert_ipynb_to_txt, convert_txt_to_ipynb


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Jupyter notebooks to/from text format for LLM processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nb4llm notebook.ipynb                    # Convert to notebook.txt
  nb4llm notebook.ipynb output.txt         # Convert to specific output file
  nb4llm --reverse notebook.txt            # Convert back to notebook.ipynb
  nb4llm --reverse notebook.txt output.ipynb  # Convert to specific output file
        """,
    )

    parser.add_argument("input_file", help="Input file (.ipynb or .txt)")

    parser.add_argument(
        "output_file",
        nargs="?",
        help="Output file (optional, auto-generated if not provided)",
    )

    parser.add_argument(
        "--reverse",
        "-r",
        action="store_true",
        help="Convert from .txt back to .ipynb (default is .ipynb to .txt)",
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    input_path = Path(args.input_file)

    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Determine conversion direction and output file
    if args.reverse:
        # txt -> ipynb
        if input_path.suffix.lower() != ".txt":
            print(
                f"Warning: Input file '{input_path}' doesn't have .txt extension",
                file=sys.stderr,
            )

        if args.output_file:
            output_path = Path(args.output_file)
        else:
            output_path = input_path.with_suffix(".ipynb")

        if args.verbose:
            print(f"Converting {input_path} -> {output_path}")

        try:
            convert_txt_to_ipynb(str(input_path), str(output_path))
            print(f"Successfully converted to {output_path}")
        except Exception as e:
            print(f"Error converting file: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        # ipynb -> txt
        if input_path.suffix.lower() != ".ipynb":
            print(
                f"Warning: Input file '{input_path}' doesn't have .ipynb extension",
                file=sys.stderr,
            )

        if args.output_file:
            output_path = Path(args.output_file)
        else:
            output_path = input_path.with_suffix(".txt")

        if args.verbose:
            print(f"Converting {input_path} -> {output_path}")

        try:
            convert_ipynb_to_txt(str(input_path), str(output_path))
            print(f"Successfully converted to {output_path}")
        except Exception as e:
            print(f"Error converting file: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
