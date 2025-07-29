import argparse
from utg_pkg.generator import traverse_and_generate_tests


def main():
    parser = argparse.ArgumentParser(
        description="Generate production-ready pytest unit tests using Google Gemini API"
    )
    parser.add_argument(
        "--source",
        type=str,
        default=".",
        help="Root directory to scan for Python files (default: .)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="tests",
        help="Directory where test files will be saved (default: tests/)",
    )

    args = parser.parse_args()
    traverse_and_generate_tests(src_root=args.source, test_root=args.output)
