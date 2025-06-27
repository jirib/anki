#!/usr/bin/env python3

import sys
import argparse
import genanki
import hashlib

def make_guid(front, back):
    """
    Make a stable GUID based on front+back text content.
    """
    return hashlib.md5((front + back).encode("utf-8")).hexdigest()

def parse_args():
    parser = argparse.ArgumentParser(description="Build an Anki .apkg from colon-separated (or other) word list")
    parser.add_argument("input", nargs="?", help="Input file (or stdin if omitted)")
    parser.add_argument("--deckname", default="My Deck", help="Deck name")
    parser.add_argument("--output", default="output.apkg", help="Output .apkg file")
    parser.add_argument("--separator", default="–", help="Field separator (default is em-dash)")
    return parser.parse_args()

def main():
    args = parse_args()

    # read input from file or stdin
    if args.input:
        with open(args.input, encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = sys.stdin.readlines()

    # create the Anki model with nicer styling
    model = genanki.Model(
      1607392319,
      'Simple Model',
      fields=[
        {'name': 'Front'},
        {'name': 'Back'},
      ],
      templates=[
        {
          'name': 'Card 1',
          'qfmt': '{{Front}}',
          'afmt': '{{Front}}<hr id="answer">{{Back}}',
        },
      ],
      css="""
      .card {
        font-family: Arial, sans-serif;
        font-size: 28px;
        text-align: center;
      }
      """
    )

    deck = genanki.Deck(
      2059400110,
      args.deckname
    )

    # process lines
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("-"):
            # remove dash
            cleaned = line.lstrip("-").strip()
            parts = cleaned.split(args.separator, 1)
            if len(parts) == 2:
                front = parts[0].strip()
                back = parts[1].strip()
                guid = make_guid(front, back)
                note = genanki.Note(
                    model=model,
                    fields=[front, back],
                    guid=guid
                )
                deck.add_note(note)

    # export
    genanki.Package(deck).write_to_file(args.output)
    print(f"Wrote {args.output} for deck: {args.deckname}")

if __name__ == "__main__":
    main()
