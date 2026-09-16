import json
import sqlite3
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from ankiscripts.core import default_templates, list_templates, load_templates

SCRIPT = Path(__file__).resolve().parents[1] / "csv2apkg.py"


def run_script(args, *, stdin=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=stdin,
        capture_output=True,
        text=True,
    )


def read_apkg(apkg_path, tmp_path):
    with zipfile.ZipFile(apkg_path) as z:
        assert "collection.anki2" in z.namelist()
        db_bytes = z.read("collection.anki2")

    db_path = tmp_path / "collection.anki2"
    db_path.write_bytes(db_bytes)

    conn = sqlite3.connect(db_path)
    models = json.loads(conn.execute("select models from col").fetchone()[0])
    notes = [row[0] for row in conn.execute("select flds from notes").fetchall()]
    conn.close()
    return models, notes


def test_default_templates():
    templates = default_templates(["Front", "Back"])
    assert templates == [
        {
            "name": "Card 1",
            "qfmt": "{{Front}}",
            "afmt": '{{Front}}<hr id="answer">{{Back}}',
        }
    ]


def test_load_templates_single_dict(tmp_path):
    path = tmp_path / "template.json"
    path.write_text(
        json.dumps({"name": "Card 1", "qfmt": "{{Q}}", "afmt": "{{A}}"}),
        encoding="utf-8",
    )
    assert load_templates(path) == [
        {"name": "Card 1", "qfmt": "{{Q}}", "afmt": "{{A}}"}
    ]


def test_load_templates_list(tmp_path):
    path = tmp_path / "template.json"
    path.write_text(
        json.dumps([{"name": "Card 1", "qfmt": "{{Q}}", "afmt": "{{A}}"}]),
        encoding="utf-8",
    )
    assert load_templates(path) == [
        {"name": "Card 1", "qfmt": "{{Q}}", "afmt": "{{A}}"}
    ]


def test_list_templates():
    assert "cli_command" in list_templates()


def test_load_templates_bundled_name():
    templates = load_templates("cli_command")
    assert templates[0]["name"] == "Card 1"
    assert templates[0]["qfmt"] == "{{question}}"
    assert "{{cli command}}" in templates[0]["afmt"]


def test_build_apkg_default(tmp_path):
    inp = tmp_path / "in.csv"
    inp.write_text("Front;Back\nhello;ahoj\nworld;svet\n", encoding="utf-8")
    out = tmp_path / "out.apkg"

    result = run_script([str(inp), "--separator", ";", "--output", str(out)])
    assert result.returncode == 0, result.stderr

    models, notes = read_apkg(out, tmp_path)
    assert len(models) == 1
    model = next(iter(models.values()))
    assert [f["name"] for f in model["flds"]] == ["Front", "Back"]
    assert [(t["name"], t["qfmt"], t["afmt"]) for t in model["tmpls"]] == [
        ("Card 1", "{{Front}}", '{{Front}}<hr id="answer">{{Back}}')
    ]
    assert notes == ["hello\x1fahoj", "world\x1fsvet"]


def test_build_apkg_custom_template(tmp_path):
    inp = tmp_path / "in.csv"
    inp.write_text("Q;A\none;two\n", encoding="utf-8")
    template = tmp_path / "template.json"
    template.write_text(
        json.dumps(
            {"name": "Reverse", "qfmt": "{{A}}", "afmt": '{{A}}<hr id="answer">{{Q}}'}
        ),
        encoding="utf-8",
    )
    out = tmp_path / "out.apkg"

    result = run_script(
        [str(inp), "--separator", ";", "--output", str(out), "--template", str(template)]
    )
    assert result.returncode == 0, result.stderr

    models, notes = read_apkg(out, tmp_path)
    model = next(iter(models.values()))
    assert [(t["name"], t["qfmt"], t["afmt"]) for t in model["tmpls"]] == [
        ("Reverse", "{{A}}", '{{A}}<hr id="answer">{{Q}}')
    ]
    assert notes == ["one\x1ftwo"]


def test_build_apkg_bundled_template(tmp_path):
    inp = tmp_path / "in.csv"
    inp.write_text("question;answer;cli command\nwhat;x;\nhow;;crm status\n", encoding="utf-8")
    out = tmp_path / "out.apkg"

    result = run_script(
        [str(inp), "--separator", ";", "--output", str(out), "--template", "cli_command"]
    )
    assert result.returncode == 0, result.stderr

    models, notes = read_apkg(out, tmp_path)
    model = next(iter(models.values()))
    assert [f["name"] for f in model["flds"]] == ["question", "answer", "cli command"]
    assert notes == ["what\x1fx\x1f", "how\x1f\x1fcrm status"]


def test_build_apkg_from_stdin(tmp_path):
    out = tmp_path / "out.apkg"
    result = run_script(
        ["--separator", ";", "--output", str(out)], stdin="Front;Back\nfoo;bar\n"
    )
    assert result.returncode == 0, result.stderr

    models, notes = read_apkg(out, tmp_path)
    assert notes == ["foo\x1fbar"]


def test_wrong_field_count_errors(tmp_path):
    inp = tmp_path / "in.csv"
    inp.write_text("Front;Back\nonly-one-field\n", encoding="utf-8")
    out = tmp_path / "out.apkg"

    result = run_script([str(inp), "--separator", ";", "--output", str(out)])
    assert result.returncode != 0
    assert "expected 2 fields, got 1" in result.stderr


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
