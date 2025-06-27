README
======

text2apkg.py
------------

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
	./text2apkg.py --deckname 'ES-apuntes' --separator '–' --output /tmp/es-apuntes.apkg 
Wrote /tmp/es-apuntes.apkg for deck: ES-apuntes
```
