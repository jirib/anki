#!/usr/bin/env python3
# /// script
# requires-python = ">3.12"
# dependencies = [
#     "genanki",
# ]
# ///

import csv
import sys
import argparse
import genanki
import hashlib
import html

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
    parser.add_argument("--separator", required=True, help="Field separator (an example: ';')")
    return parser.parse_args()

def main():
    args = parse_args()

    # read input from file or stdin
    if args.input:
        with open(args.input, encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter=args.separator)
            header = next(reader)  # first line = field names
            rows = list(reader)

    field_names = [h.strip() for h in header]
    
    # create the Anki model with nicer styling
    model = genanki.Model(
      1607392319,
      'text2anki_py',
      fields=[{'name': name} for name in field_names],
      templates=[
        {
          'name': 'Card 1',
          'qfmt': '{{' + field_names[0] + '}}',
          'afmt': '{{' + field_names[0] + '}}<hr id="answer">{{' + field_names[1] + '}}',
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

    expected = len(field_names)
    
    # process lines
    for lineno, row in enumerate(rows, start=2):
        if len(row) != expected:
            raise ValueError(
                f'Line {{lineno}}: expected {expected} fields, got {len(row)}'
            )

        fields = [html.escape(col.strip()) for col in row]
        
        guid = hashlib.md5(''.join(fields).encode('utf-8')).hexdigest()
        
        note = genanki.Note(
                model=model,
                fields=fields,
                guid=guid
            )
        
        deck.add_note(note)

    # export
    genanki.Package(deck).write_to_file(args.output)
    print(f"Wrote {args.output} for deck: {args.deckname}")

if __name__ == "__main__":
    main()
