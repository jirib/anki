"""Build an Anki .apkg deck from a CSV (or similar) file."""

import argparse
import csv
import sys

from ankiscripts.core import build_apkg, list_templates, list_templates_with_paths


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Build an Anki .apkg from a CSV (or similar) file"
    )
    parser.add_argument("input", nargs="?", help="Input file (or stdin if omitted)")
    parser.add_argument("--deckname", default="My Deck", help="Deck name")
    parser.add_argument("--output", default="output.apkg", help="Output .apkg file")
    parser.add_argument("--separator", help="Field separator (an example: ';')")
    parser.add_argument(
        "--template",
        help=(
            "Card template: a path to a JSON file or a bundled template name "
            f"({', '.join(list_templates())}). Defaults to a Front/Back card."
        ),
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List bundled template names and their paths, then exit.",
    )
    args = parser.parse_args(argv)
    if not args.list_templates and not args.separator:
        parser.error("--separator is required")
    return args


def read_csv(source, separator):
    reader = csv.reader(source, delimiter=separator)
    header = next(reader)
    field_names = [h.strip() for h in header]
    rows = list(reader)
    return field_names, rows


def main(argv=None):
    args = parse_args(argv)

    if args.list_templates:
        for name, path in list_templates_with_paths():
            print(f"{name}\t{path}")
        return 0

    if args.input:
        with open(args.input, encoding="utf-8", newline="") as f:
            field_names, rows = read_csv(f, args.separator)
    else:
        field_names, rows = read_csv(sys.stdin, args.separator)

    build_apkg(
        field_names,
        rows,
        deckname=args.deckname,
        output=args.output,
        model_name="csv2anki_py",
        template=args.template,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
