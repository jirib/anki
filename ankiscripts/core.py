"""Shared helpers for building Anki .apkg packages from tabular data."""

import hashlib
import html
import json
from importlib import resources
from pathlib import Path

import genanki

PACKAGE = "ankiscripts"

DEFAULT_CSS = """
.card {
  font-family: Arial, sans-serif;
  font-size: 28px;
  text-align: center;
}
"""


def _stable_id(seed: str, *, salt: str) -> int:
    h = hashlib.sha1((salt + "\x1f" + seed).encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def default_templates(field_names):
    front = "{{" + field_names[0] + "}}"
    back = "{{" + field_names[1] + "}}"
    return [
        {
            "name": "Card 1",
            "qfmt": front,
            "afmt": front + '<hr id="answer">' + back,
        },
    ]


def templates_dir():
    return resources.files(PACKAGE) / "templates"


def template_path(name):
    return templates_dir() / f"{name}.json"


def list_templates():
    return sorted(
        p.name.removesuffix(".json")
        for p in templates_dir().iterdir()
        if p.name.endswith(".json")
    )


def list_templates_with_paths():
    return [(name, str(template_path(name))) for name in list_templates()]


def _load_json_text(text):
    data = json.loads(text)
    if isinstance(data, dict):
        return [data]
    return data


def load_templates(template):
    """Resolve a --template value to a list of card template dicts.

    Accepts a path to a JSON file or a bundled template name (e.g. ``cli_command``).
    """
    if template is None:
        return None

    path = Path(template)
    if path.is_file():
        return _load_json_text(path.read_text(encoding="utf-8"))

    name = str(template).removesuffix(".json")
    bundled = template_path(name)
    if bundled.is_file():
        return _load_json_text(bundled.read_text(encoding="utf-8"))

    available = ", ".join(list_templates())
    raise FileNotFoundError(
        f"Template {template!r} not found (not a file, and not one of: {available})"
    )


def build_apkg(
    field_names,
    rows,
    *,
    deckname,
    output,
    model_name,
    template=None,
    css=DEFAULT_CSS,
):
    templates = load_templates(template) if template else default_templates(field_names)

    model = genanki.Model(
        _stable_id(model_name, salt="model"),
        model_name,
        fields=[{"name": name} for name in field_names],
        templates=templates,
        css=css,
    )

    deck = genanki.Deck(_stable_id(deckname, salt="deck"), deckname)

    expected = len(field_names)
    for lineno, row in enumerate(rows, start=2):
        if len(row) != expected:
            raise ValueError(f"Line {lineno}: expected {expected} fields, got {len(row)}")

        fields = [html.escape(str(col).strip()) for col in row]
        guid = hashlib.md5("".join(fields).encode("utf-8")).hexdigest()
        deck.add_note(genanki.Note(model=model, fields=fields, guid=guid))

    genanki.Package(deck).write_to_file(output)
    print(f"Wrote {output} for deck: {deckname}")
