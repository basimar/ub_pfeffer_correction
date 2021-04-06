#!/usr/bin/python3

# Skript filtert Felder gemäss Tabelle in https://wiki.biozentrum.unibas.ch/display/UBIT/Aleph%3A+Pfeffer-Bereinigung aus Aufnahmen hinaus. Dazu liest es via STDIN einen aufbereiteten Dump (vgl. Anleitung in Wiki-Artikel) ein und gibt das gefilterte Set via STDOUT wieder aus.

import fileinput
import re
import sys


def create_lookup_set(input_file):
    print('Loading {}'.format(input_file), file=sys.stderr)
    lookup_set = set()
    with open(input_file) as f:
        for sysno in f:
            lookup_set.add(sysno[0:9])
    print('Loading finished. Lookup contains {} keys'.format(len(lookup_set)), file=sys.stderr)
    return lookup_set


def get_field(line):
    return line[10:15]


def get_sysno(line):
    return line[0:9]


def rvk_field(line):
    return get_field(line) == '084  ' and '$$2rvk' in line[18:] and get_sysno(line) in rvk_lookup


def ddc_field(line):
    return get_field(line) == '0820 ' and get_sysno(line) in ddc_lookup


def mesh_field(line):
    return get_field(line) in ['650 2', '651 2', '655 2'] and get_sysno(line) in mesh_lookup


def gnd_field(line, lookup):
    return get_field(line) in ['60007', '60017', '60037', '600 7', '61017',
                               '61027', '61127', '630 7', '648 7', '650 7', '651 7'] and get_sysno(line) in lookup


def genre_field(line, lookup):
    """
    Return field 655_7 unless
    - content of $a is in blacklist or
    - record falls in the category "Keine ISBN, Rest"
    """
    blacklist = re.compile(r"""\$\$a
	(Altkarte|
	Ausstellungskatalog|
	Autobiografie|
	Bibliografie|
	Biografie|
	Bildband|
	Briefsammlung|
	CD|
	CD-ROM|
	Comic|
	Festschrift|
	Hochschulschrift|
	Hörbuch|
	Karte|
	Konferenzschrift|
	Monografische\ Reihe|
	Schulbuch|
	Webseite|
	Zeitschrift|
	Zeitung)
	[\Z$]""", re.VERBOSE)
    return get_field(line) == '655 7' and get_sysno(line) not in lookup and not blacklist.search(line[18:])


rvk_lookup = create_lookup_set('imported_fields/imported_rvk.sys')
ddc_lookup = create_lookup_set('imported_fields/imported_ddc.sys')
mesh_lookup = create_lookup_set('imported_fields/imported_mesh_isbn_subjects.sys')
gnd_lookup = create_lookup_set('imported_fields/imported_gnd_isbn_subjects.sys')
gnd_rest_lookup = create_lookup_set('imported_fields/imported_gnd_rest.sys')

for l in fileinput.input():
    l = l.rstrip('\r\n')

    if gnd_field(l, gnd_rest_lookup):
        field = get_field(l)
        subfields = '$$'.join([sf for sf in l[18:].split(
            "$$") if not (sf.startswith('1') or sf.startswith('2'))])
        print('{} {}4 {} {}'.format(l[0:9], field[0:4], l[16], subfields))
    # Print anything which should 
    elif not rvk_field(l) and not ddc_field(l) and not mesh_field(l) and not gnd_field(l, gnd_lookup) and not genre_field(l, gnd_rest_lookup):
        print(l)
