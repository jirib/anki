# ankiscripts

Build Anki `.apkg` decks from CSV or Excel sources.

## Install

``` shell
pipx install .
# or, in development:
mise install
```

This provides two commands: `csv2apkg` and `xlsx2apkg`.

## Card templates

`--template` accepts either a path to a JSON file or the name of a bundled
template (stored in `ankiscripts/templates/` and installed with the package):

``` shell
csv2apkg --list-templates
csv2apkg words.csv --separator ',' --template cli_command --output deck.apkg
```

## csv2apkg

``` shell
# the input is an ODT
$ pandoc --wrap=none -f odt -t plain /tmp/Apuntes\ de\ las\ clases\ con\ Jiří.odt | \
    grep -P '^\s*-' | \
	sed 's/^- *//' | head
lejos – daleko
lejos de – daleko od (něčeho)
allí – tam
a veces – někdy
nunca – nikdy
luego – potom
hasta – až do
pronto – brzy
un poco (de) – trochu (něčeho)
No sé. – Nevím.

$ pandoc --wrap=none -f odt -t plain /tmp/Apuntes\ de\ las\ clases\ con\ Jiří.odt | \
    grep -P '^\s*-' | \
	sed 's/^- *//' | \
	csv2apkg --deckname 'ES-apuntes' --separator '–' --output /tmp/es-apuntes.apkg 
Wrote /tmp/es-apuntes.apkg for deck: ES-apuntes
```

## xlsx2apkg

``` shell
xlsx2apkg deck.xlsx --sheet Sheet1 --template cli_command --output deck.apkg
```

