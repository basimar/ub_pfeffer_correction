#!/usr/bin/env python3

# Skript filtert Felder gemäss Tabelle in
# https://wiki.biozentrum.unibas.ch/display/UBIT/Aleph%3A+Pfeffer-Bereinigung aus Aufnahmen hinaus.
# Dazu liest es via STDIN einen aufbereiteten Dump (vgl. Anleitung in Wiki-Artikel) ein und gibt das gefilterte Set via
# STDOUT wieder aus. Über STDERR werden Statistiken zu den einzelnen Schlagwörtern ausgegeben
# (ign = ignored, ret = retained, del = deleted)

import fileinput
import re
import sys
from itertools import chain


def get_possible_sysnos(subject_heading, path_of_root):
    filepaths = {
        'Altkarte': '{}/655_Altkarte.sys'.format(path_of_root),
        'Ausstellungskatalog': '{}/655_Ausstellung.sys'.format(path_of_root),
        'Briefsammlung': '{}/655_Briefsammlung.sys'.format(path_of_root),
        'CD': '{}/655_CD.sys'.format(path_of_root),
        'CD-ROM': '{}/655_CD-ROM.sys'.format(path_of_root),
        'Comic': '{}/655_Comic.sys'.format(path_of_root),
        'DVD-ROM': '{}/655_DVD-ROM.sys'.format(path_of_root),
        'DVD-Video': '{}/655_DVD-Video.sys'.format(path_of_root),
        'Karte': '{}/655_Karte.sys'.format(path_of_root),
        'Konferenzschrift': '{}/655_Kongress.sys'.format(path_of_root),
        'Schallplatte': '{}/655_Schallplatte.sys'.format(path_of_root),
        'Videokassette': '{}/655_Videokassette.sys'.format(path_of_root),
        'Weltkarte': '{}/655_Weltkarte.sys'.format(path_of_root),
        'Zeitschrift': '{}/655_Zeitschrift.sys'.format(path_of_root)
    }
    with open(filepaths[subject_heading]) as f:
        return set([li.strip('\r\n') for li in f])


def create_913_catalogue(filepath):
    """
    Creates a lookup table which is needed for subsequent comparison of subject headings
    :param filepath: path to an extract of content of 913 fields
    :return: lookup table
    """
    catalogue_913 = dict()
    pattern_a = re.compile(r"\$\$a([^\\Z$]+)")
    pattern_b = re.compile(r"\$\$b([^\\Z$]+)")
    with open(filepath) as f:
        for li in f:
            key = li[:9]
            value = [{
                'a': pattern_a.findall(li[16:]),
                'b': pattern_b.findall(li[16:])
            }]
            if key in catalogue_913:
                catalogue_913[key].extend(value)
            else:
                catalogue_913[key] = value
    return catalogue_913


def has_any_term_in_subfields(termlist, fieldlist, record):
    for f in fieldlist:
        sv = get_subfield_values_of_lines(get_lines_of_field(f, record), 'a')
        if f == '245':
            sv.extend(get_subfield_values_of_lines(get_lines_of_field(f, record), 'b'))
            sv.extend(get_subfield_values_of_lines(get_lines_of_field(f, record), 'i'))
            sv.extend( get_subfield_values_of_lines(get_lines_of_field(f, record), 'j'))
            sv.extend(get_subfield_values_of_lines(get_lines_of_field(f, record), 'p'))
        if f == '505':
            sv.extend(get_subfield_values_of_lines(get_lines_of_field(f, record), 'g'))
            sv.extend(get_subfield_values_of_lines(get_lines_of_field(f, record), 'r'))
            sv.extend(get_subfield_values_of_lines(get_lines_of_field(f, record), 't'))
        for m in sv:
            for t in termlist:
                if re.search(t, m, re.IGNORECASE):
                    return True
    return False


def has_value_in_subfield(record_line, field, subfield, value):
    return ((record_line[10:13] == field if len(field) == 3 else record_line[10:15] == field) and
            '$${}{}'.format(subfield, value) in record_line[18:])


def has_value_in_position(record_line, field, position, value):
    return record_line[10:13] == field and record_line[18:][position] == value


def has_values_in_ldr_6(record_line, values):
    for val in values:
        if has_value_in_position(record_line, 'LDR', 6, val):
            return True
    return False


def has_value_in_field_posi(lines, value, field, posi):
    for li in lines:
        if has_value_in_position(li, field, posi, value):
            return True
    return False


def has_value_in_007_0(lines, value):
    return has_value_in_field_posi(lines, value, '007', 0)


def has_value_in_007_1(lines, value):
    return has_value_in_field_posi(lines, value, '007', 1)


def has_value_in_007_3(lines, value):
    return has_value_in_field_posi(lines, value, '007', 3)


def has_value_in_007_4(lines, value):
    return has_value_in_field_posi(lines, value, '007', 4)


def has_value_in_008_21(lines, value):
    return has_value_in_field_posi(lines, value, '008', 21)


def has_value_in_008_24(lines, value):
    return has_value_in_field_posi(lines, value, '008', 24)


def has_value_in_008_25(lines, value):
    return has_value_in_field_posi(lines, value, '008', 25)


def has_value_in_008_26(lines, value):
    return has_value_in_field_posi(lines, value, '008', 26)


def has_value_in_008_27(lines, value):
    return has_value_in_field_posi(lines, value, '008', 27)


def has_value_in_008_29(lines, value):
    return has_value_in_field_posi(lines, value, '008', 29)


def has_value_in_008_33(lines, value):
    return has_value_in_field_posi(lines, value, '008', 33)


def has_value_in_906(lines, subfield, value):
    for li in lines:
        if has_value_in_subfield(li, '906', subfield, value):
            return True
    return False


def has_value_in_907(lines, subfield, value):
    for li in lines:
        if has_value_in_subfield(li, '907', subfield, value):
            return True
    return False


def has_field_913(lines):
    for li in lines:
        if li[10:13] == '913':
            return True
    return False


def has_identical_913_field(sysno, value_a, value_655_y, catalogue_913):
    if sysno in catalogue_913:
        for value_b in [e['b'] for e in catalogue_913[sysno] if value_a in e['a']]:
            if value_655_y in value_b:
                return True
    return False


def get_655_y_for_subject(subject, record):
    return list(chain.from_iterable([re.findall(r"\$\$y([^\\Z$]+)", li[18:]) for li in record if
                                     li[10:15] == '655 7' and '$$a{}'.format(subject) in li[18:] and re.search(
                                         r"\$\$y([^\\Z$]+)", li[18:])]))


def get_lines_of_field(field, record):
    return [li for li in record if (li[10:13] == field if len(field) == 3 else li[10:15] == field)]


def get_subfield_values_of_lines(lines, subfield):
    results = []
    for li in lines:
        results.extend(re.findall(r"\$\$" + subfield + r"([^\\Z$]+)", li))
    return results


def remove_subject_from_record(subject, record):
    return [li for li in record if not (li[10:15] == '655 7' and '$$a{}'.format(subject) in li[18:])]


def remove_subject_with_year_from_record(subject, year, record):
    return [li for li in record if
            not (li[10:15] == '655 7' and '$$a{}'.format(subject) in li[18:] and '$$y{}'.format(year) in li[18:])]


def move_to_655__4_and_remove_subfields_1_2(subject, record):
    new_list = []
    regex = re.compile(r"\$\$[12][^$]+")
    for li in record:
        if li[10:15] == '655 7' and '$$a{}'.format(subject) in li[18:]:
            new_list.append(li[:10] + '655 4 ' + regex.sub('', li[16:]))
        else:
            new_list.append(li)
    return new_list


def write_record_to_file(handler, record):
    for li in record:
        handler.write(li + '\n')


def filter_altkarte(record):
    removed_655 = False
    ldr_lines = has_values_in_ldr_6(get_lines_of_field('LDR', record)[0], ['e', 'f']) if len(
        get_lines_of_field('LDR', record)) else False
    if not ((ldr_lines and
             has_value_in_007_1(get_lines_of_field('007', record), 'j')) or
            has_value_in_906(get_lines_of_field('906', record), 'c', 'CM Karte = Carte') or
            has_value_in_907(get_lines_of_field('907', record), 'c', 'CM Karte = Carte')):
        record = remove_subject_from_record('Altkarte', record)
        removed_655 = True
    else:
        record = move_to_655__4_and_remove_subfields_1_2('Altkarte', record)
    return record, removed_655


def filter_ausstellungskatalog(record, catalogue_913, out_file_deleted, out_file_retained):
    removed_655 = dict()
    uncontrolled_terms = ['ausstellung',
                          'exhibition',
                          'exposition',
                          'museum',
                          'musée',
                          'kunststiftung',
                          'kunsthalle',
                          'galerie',
                          'gallery']
    sysno = record[0][:9]
    ausstellungskatalog_in_6xx_d_ = [li for li in record if
                                     li[10] == '6' and li[13:15] == 'D ' and '$$vAusstellungskatalog' in li[18:]]

    if (sysno not in catalogue_913 and
            (ausstellungskatalog_in_6xx_d_ or
             has_any_term_in_subfields(uncontrolled_terms, ['245', '500'], record))):
        write_record_to_file(out_file_retained, record)
    elif sysno in catalogue_913:
        out_file_deleted_written = False
        out_file_retained_written = False
        subfields_655_y = get_655_y_for_subject('Ausstellungskatalog', record)
        for subfield_655_y in subfields_655_y:
            if has_identical_913_field(sysno, 'Ausstellung = Exposition', subfield_655_y, catalogue_913):
                removed_655[subfield_655_y] = False
                if not out_file_retained_written:
                    write_record_to_file(out_file_retained, record)
                    out_file_retained_written = True
            else:
                record = remove_subject_with_year_from_record('Ausstellungskatalog', subfield_655_y, record)
                removed_655[subfield_655_y] = True
                if not out_file_deleted_written:
                    write_record_to_file(out_file_deleted, record)
                    out_file_deleted_written = True
    else:
        write_record_to_file(out_file_deleted, record)
        record = remove_subject_from_record('Ausstellungskatalog', record)
        removed_655['ALL'] = 'ALL'

    return record, removed_655


def filter_briefsammlung(record, out_file_deleted, out_file_retained):
    removed_655 = False
    uncontrolled_terms = ['briefe',
                          'briefwechsel',
                          'letters',
                          'correspondence',
                          'correspondances',
                          'lettere',
                          'lettre',
                          'korrespondenz',
                          'correspondenzen']
    ldr_lines = has_values_in_ldr_6(get_lines_of_field('LDR', record)[0], ['i', 'j']) if len(
        get_lines_of_field('LDR', record)) else False
    if not ((ldr_lines and
             has_value_in_008_33(get_lines_of_field('008', record), 'i')) or
            has_value_in_906(get_lines_of_field('906', record), 'a', 'Briefe = Correspondance') or
            has_value_in_907(get_lines_of_field('907', record), 'a', 'Briefe = Correspondance') or
            has_any_term_in_subfields(uncontrolled_terms, ['245', '500'], record)):
        write_record_to_file(out_file_deleted, record)
        record = remove_subject_from_record('Briefsammlung', record)
        removed_655 = True
    else:
        write_record_to_file(out_file_retained, record)
    return record, removed_655


def filter_cd(record):
    removed_655 = False
    if not (has_value_in_906(get_lines_of_field('906', record), 'e', 'SR CD') or
            has_value_in_907(get_lines_of_field('907', record), 'e', 'SR CD')):
        record = remove_subject_from_record('CD', record)
        removed_655 = True
    else:
        record = move_to_655__4_and_remove_subfields_1_2('CD', record)
    return record, removed_655


def filter_cdrom(record):
    removed_655 = False
    if not (has_value_in_906(get_lines_of_field('906', record), 'g', 'CF CD-ROM = Cédérom') or
            has_value_in_907(get_lines_of_field('907', record), 'g', 'CF CD-ROM = Cédérom')):
        record = remove_subject_from_record('CD-ROM', record)
        removed_655 = True
    else:
        record = move_to_655__4_and_remove_subfields_1_2('CD-ROM', record)
    return record, removed_655


def filter_comic(record, out_file_deleted, out_file_retained):
    removed_655 = False
    uncontrolled_terms = ['comic',
                          'asterix',
                          'graphic novel']
    if not (has_value_in_008_24(get_lines_of_field('008', record), '6') or
            has_value_in_008_25(get_lines_of_field('008', record), '6') or
            has_value_in_008_26(get_lines_of_field('008', record), '6') or
            has_value_in_008_27(get_lines_of_field('008', record), '6') or
            has_any_term_in_subfields(uncontrolled_terms, ['245', '490', '500'], record)):
        write_record_to_file(out_file_deleted, record)
        record = remove_subject_from_record('Comic', record)
        removed_655 = True
    else:
        write_record_to_file(out_file_retained, record)
    return record, removed_655


def filter_dvdrom(record, out_file_deleted, out_file_retained):
    removed_655 = False
    if not (has_value_in_906(get_lines_of_field('906', record), 'g', 'CF DVD-ROM') or
            has_value_in_907(get_lines_of_field('907', record), 'g', 'CF DVD-ROM')):
        write_record_to_file(out_file_deleted, record)
        record = remove_subject_from_record('DVD-ROM', record)
        removed_655 = True
    else:
        record = move_to_655__4_and_remove_subfields_1_2('DVD-ROM', record)
        write_record_to_file(out_file_retained, record)
    return record, removed_655


def filter_dvdvideo(record, out_file_deleted, out_file_retained):
    removed_655 = False
    if not (has_value_in_008_33(get_lines_of_field('008', record), 'v') or
            (has_value_in_007_0(get_lines_of_field('007', record), 'f') and
             has_value_in_007_1(get_lines_of_field('007', record), 'd') and
             has_value_in_007_4(get_lines_of_field('007', record), 'v')) or
            has_value_in_906(get_lines_of_field('906', record), 'h', 'MP DVD-Video') or
            has_value_in_907(get_lines_of_field('907', record), 'h', 'MP DVD-Video')):
        write_record_to_file(out_file_deleted, record)
        record = remove_subject_from_record('DVD-Video', record)
        removed_655 = True
    else:
        record = move_to_655__4_and_remove_subfields_1_2('DVD-Video', record)
        write_record_to_file(out_file_retained, record)
    return record, removed_655


def filter_karte(record):
    removed_655 = False
    ldr_lines = has_values_in_ldr_6(get_lines_of_field('LDR', record)[0], ['e', 'f']) if len(
        get_lines_of_field('LDR', record)) else False
    if not ((ldr_lines and
             has_value_in_007_1(get_lines_of_field('007', record), 'j')) or
            has_value_in_906(get_lines_of_field('906', record), 'c', 'CM Karte = Carte') or
            has_value_in_907(get_lines_of_field('907', record), 'c', 'CM Karte = Carte')):
        record = remove_subject_from_record('Karte', record)
        removed_655 = True
    else:
        record = move_to_655__4_and_remove_subfields_1_2('Karte', record)
    return record, removed_655


def filter_konferenzschrift(record, catalogue_913, out_file_deleted, out_file_retained):
    removed_655 = dict()
    uncontrolled_terms = ['jahrestagung',
                          'conference',
                          'conférence',
                          'konferenz',
                          'congress',
                          'kongress',
                          'proceedings',
                          'colloque',
                          'convegno']
    sysno = record[0][:9]
    if (sysno not in catalogue_913 and
            (has_value_in_008_29(get_lines_of_field('008', record), '1') or
             has_any_term_in_subfields(uncontrolled_terms, ['245', '490', '500'], record))):
        write_record_to_file(out_file_retained, record)
    elif sysno in catalogue_913:
        out_file_deleted_written = False
        out_file_retained_written = False
        subfields_655_y = get_655_y_for_subject('Konferenzschrift', record)
        for subfield_655_y in subfields_655_y:
            if has_identical_913_field(sysno, 'Kongress = Congrès', subfield_655_y, catalogue_913):
                removed_655[subfield_655_y] = False
                if not out_file_retained_written:
                    write_record_to_file(out_file_retained, record)
                    out_file_retained_written = True
            else:
                record = remove_subject_with_year_from_record('Konferenzschrift', subfield_655_y, record)
                removed_655[subfield_655_y] = True
                if not out_file_deleted_written:
                    write_record_to_file(out_file_deleted, record)
                    out_file_deleted_written = True
    else:
        write_record_to_file(out_file_deleted, record)
        record = remove_subject_from_record('Konferenzschrift', record)
        removed_655['ALL'] = 'ALL'
    return record, removed_655


def filter_schallplatte(record, out_file_deleted, out_file_retained):
    removed_655 = False
    if not ((has_value_in_007_0(get_lines_of_field('007', record), 's') and
             has_value_in_007_1(get_lines_of_field('007', record), 'd') and
             (has_value_in_007_3(get_lines_of_field('007', record), 'b') or
              has_value_in_007_3(get_lines_of_field('007', record), 'c') or
              has_value_in_007_3(get_lines_of_field('007', record), 'd'))) or
            has_value_in_906(get_lines_of_field('906', record), 'e', 'SR Schallplatte = Disque*') or
            has_value_in_907(get_lines_of_field('907', record), 'e', 'SR Schallplatte = Disque*')):
        write_record_to_file(out_file_deleted, record)
        record = remove_subject_from_record('Schallplatte', record)
        removed_655 = True
    else:
        record = move_to_655__4_and_remove_subfields_1_2('Schallplatte', record)
        write_record_to_file(out_file_retained, record)
    return record, removed_655


def filter_videokassette(record, out_file_deleted, out_file_retained):
    removed_655 = False
    if not (has_value_in_008_33(get_lines_of_field('008', record), 'v') or
            (has_value_in_007_0(get_lines_of_field('007', record), 'v') and
             has_value_in_007_1(get_lines_of_field('007', record), 'f')) or
            has_value_in_906(get_lines_of_field('906', record), 'h', 'MP Videoaufzeichnung = Vidéo') or
            has_value_in_907(get_lines_of_field('906', record), 'h', 'MP Videoaufzeichnung = Vidéo')):
        write_record_to_file(out_file_deleted, record)
        record = remove_subject_from_record('Videokassette', record)
        removed_655 = True
    else:
        record = move_to_655__4_and_remove_subfields_1_2('Videokassette', record)
        write_record_to_file(out_file_retained, record)
    return record, removed_655


def filter_weltkarte(record):
    removed_655 = False
    ldr_lines = has_values_in_ldr_6(get_lines_of_field('LDR', record)[0], ['e', 'f']) if len(
        get_lines_of_field('LDR', record)) else False
    if not ((ldr_lines and has_value_in_007_1(get_lines_of_field('007', record), 'j')) or
            has_value_in_906(get_lines_of_field('906', record), 'c', 'CM Karte = Carte') or
            has_value_in_907(get_lines_of_field('907', record), 'c', 'CM Karte = Carte')):
        record = remove_subject_from_record('Weltkarte', record)
        removed_655 = True
    else:
        record = move_to_655__4_and_remove_subfields_1_2('Weltkarte', record)
    return record, removed_655


def filter_zeitschrift(record, out_file_deleted, out_file_retained):
    removed_655 = False
    if not has_value_in_008_21(get_lines_of_field('008', record), 'p'):
        write_record_to_file(out_file_deleted, record)
        record = remove_subject_from_record('Zeitschrift', record)
        removed_655 = True
    else:
        write_record_to_file(out_file_retained, record)
    return record, removed_655


if __name__ == "__main__":
    rootpath = '/opt/scripts/pfeffer_correction/imported_fields_655'
    # path_to_913_list = '{}/913.seq'.format(rootpath)

    # cat_913 = create_913_catalogue(path_to_913_list)

    # altkarte_sysnos = get_possible_sysnos('Altkarte', rootpath)
    # ausstellungskatalog_sysnos = get_possible_sysnos('Ausstellungskatalog', rootpath)
    # briefsammlung_sysnos = get_possible_sysnos('Briefsammlung', rootpath)
    cd_sysnos = get_possible_sysnos('CD', rootpath)
    cdrom_sysnos = get_possible_sysnos('CD-ROM', rootpath)
    # comic_sysnos = get_possible_sysnos('Comic', rootpath)
    # dvdrom_sysnos = get_possible_sysnos('DVD-ROM', rootpath)
    # dvdvideo_sysnos = get_possible_sysnos('DVD-Video', rootpath)
    # karte_sysnos = get_possible_sysnos('Karte', rootpath)
    # konferenzschrift_sysnos = get_possible_sysnos('Konferenzschrift', rootpath)
    # schallplatte_sysnos = get_possible_sysnos('Schallplatte', rootpath)
    # videokassette_sysnos = get_possible_sysnos('Videokassette', rootpath)
    # weltkarte_sysnos = get_possible_sysnos('Weltkarte', rootpath)
    zeitschrift_sysnos = get_possible_sysnos('Zeitschrift', rootpath)

    current_sysno = ''
    current_record = []

    # out_ausstellungskatalog_deleted = open('ausstellungskatalog_deleted.seq', 'w')
    # out_ausstellungskatalog_retained = open('ausstellungskatalog_retained.seq', 'w')
    # out_briefsammlung_deleted = open('briefsammlung_deleted.seq', 'w')
    # out_briefsammlung_retained = open('briefsammlung_retained.seq', 'w')
    # out_comic_deleted = open('comic_deleted.seq', 'w')
    # out_comic_retained = open('comic_retained.seq', 'w')
    # out_dvdrom_deleted = open('dvdrom_deleted.seq', 'w')
    # out_dvdrom_retained = open('dvdrom_retained.seq', 'w')
    # out_dvdvideo_deleted = open('dvdvideo_deleted.seq', 'w')
    # out_dvdvideo_retained = open('dvdvideo_retained.seq', 'w')
    # out_konferenzschrift_deleted = open('konferenzschrift_deleted.seq', 'w')
    # out_konferenzschrift_retained = open('konferenzschrift_retained.seq', 'w')
    # out_schallplatte_deleted = open('schallplatte_deleted.seq', 'w')
    # out_schallplatte_retained = open('schallplatte_retained.seq', 'w')
    # out_videokassette_deleted = open('videokassette_deleted.seq', 'w')
    # out_videokassette_retained = open('videokassette_retained.seq', 'w')
    out_zeitschrift_deleted = open('zeitschrift_deleted.seq', 'w')
    out_zeitschrift_retained = open('zeitschrift_retained.seq', 'w')

    for line in fileinput.input():
        line = line.rstrip('\r\n')
        if current_sysno == '':
            current_sysno = line[0:9]
            current_record.append(line)
        elif line.startswith(current_sysno):
            current_record.append(line)
        else:
            # if current_sysno in altkarte_sysnos:
            #     current_record, removed = filter_altkarte(current_record)
            #     print('{}\t{}\t{}'.format(current_sysno, 'Altkarte', 'del' if removed else 'ret'), file=sys.stderr)
            # else:
            #     print('{}\t{}\t{}'.format(current_sysno, 'Altkarte', 'ign'), file=sys.stderr)
            # if current_sysno in ausstellungskatalog_sysnos:
            #     current_record, removed = filter_ausstellungskatalog(current_record, cat_913,
            #                                                          out_ausstellungskatalog_deleted,
            #                                                          out_ausstellungskatalog_retained)
            #     if len(removed):
            #         for k, v in removed.items():
            #             if k == 'ALL':
            #                 print('{}\t{}\t{}'.format(current_sysno, 'Ausstellungskatalog', 'del'),
            #                       file=sys.stderr)
            #             else:
            #                 print(
            #                     '{}\t{}\t{}'.format(current_sysno, 'Ausstellungskatalog//' + k, 'del' if v else 'ret'),
            #                     file=sys.stderr)
            #     else:
            #         print('{}\t{}\t{}'.format(current_sysno, 'Ausstellungskatalog', 'ret'),
            #               file=sys.stderr)
            #
            # else:
            #     print('{}\t{}\t{}'.format(current_sysno, 'Ausstellungskatalog', 'ign'), file=sys.stderr)
            # if current_sysno in briefsammlung_sysnos:
            #     current_record, removed = filter_briefsammlung(current_record, out_briefsammlung_deleted,
            #                                                    out_briefsammlung_retained)
            #     print('{}\t{}\t{}'.format(current_sysno, 'Briefsammlung', 'del' if removed else 'ret'), file=sys.stderr)
            # else:
            #     print('{}\t{}\t{}'.format(current_sysno, 'Briefsammlung', 'ign'), file=sys.stderr)
            if current_sysno in cd_sysnos:
                current_record, removed = filter_cd(current_record)
                print('{}\t{}\t{}'.format(current_sysno, 'CD', 'del' if removed else 'ret'), file=sys.stderr)
            else:
                print('{}\t{}\t{}'.format(current_sysno, 'CD', 'ign'), file=sys.stderr)
            if current_sysno in cdrom_sysnos:
                current_record, removed = filter_cdrom(current_record)
                print('{}\t{}\t{}'.format(current_sysno, 'CD-ROM', 'del' if removed else 'ret'), file=sys.stderr)
            else:
                print('{}\t{}\t{}'.format(current_sysno, 'CD-ROM', 'ign'), file=sys.stderr)
            # if current_sysno in comic_sysnos:
            #     current_record, removed = filter_comic(current_record, out_comic_deleted, out_comic_retained)
            #     print('{}\t{}\t{}'.format(current_sysno, 'Comic', 'del' if removed else 'ret'), file=sys.stderr)
            # else:
            #     print('{}\t{}\t{}'.format(current_sysno, 'Comic', 'ign'), file=sys.stderr)
            # if current_sysno in dvdrom_sysnos:
            #     current_record, removed = filter_dvdrom(current_record, out_dvdrom_deleted, out_dvdrom_retained)
            #     print('{}\t{}\t{}'.format(current_sysno, 'DVD-ROM', 'del' if removed else 'ret'), file=sys.stderr)
            # else:
            #     print('{}\t{}\t{}'.format(current_sysno, 'DVD-ROM', 'ign'), file=sys.stderr)
            # if current_sysno in dvdvideo_sysnos:
            #     current_record, removed = filter_dvdvideo(current_record, out_dvdvideo_deleted, out_dvdvideo_retained)
            #     print('{}\t{}\t{}'.format(current_sysno, 'DVD-Video', 'del' if removed else 'ret'), file=sys.stderr)
            # else:
            #     print('{}\t{}\t{}'.format(current_sysno, 'DVD-Video', 'ign'), file=sys.stderr)
            # if current_sysno in karte_sysnos:
            #     current_record, removed = filter_karte(current_record)
            #     print('{}\t{}\t{}'.format(current_sysno, 'Karte', 'del' if removed else 'ret'), file=sys.stderr)
            # else:
            #     print('{}\t{}\t{}'.format(current_sysno, 'Karte', 'ign'), file=sys.stderr)
            # if current_sysno in konferenzschrift_sysnos:
            #     current_record, removed = filter_konferenzschrift(current_record, cat_913,
            #                                                       out_konferenzschrift_deleted,
            #                                                       out_konferenzschrift_retained)
            #     if len(removed):
            #         for k, v in removed.items():
            #             if k == 'ALL':
            #                 print('{}\t{}\t{}'.format(current_sysno, 'Konferenzschrift', 'del'),
            #                       file=sys.stderr)
            #             else:
            #                 print(
            #                     '{}\t{}\t{}'.format(current_sysno, 'Konferenzschrift//' + k, 'del' if v else 'ret'),
            #                     file=sys.stderr)
            #     else:
            #         print('{}\t{}\t{}'.format(current_sysno, 'Konferenzschrift', 'ret'),
            #               file=sys.stderr)
            # else:
            #     print('{}\t{}\t{}'.format(current_sysno, 'Konferenzschrift', 'ign'), file=sys.stderr)
            # if current_sysno in schallplatte_sysnos:
            #     current_record, removed = filter_schallplatte(current_record, out_schallplatte_deleted,
            #                                                   out_schallplatte_retained)
            #     print('{}\t{}\t{}'.format(current_sysno, 'Schallplatte', 'del' if removed else 'ret'), file=sys.stderr)
            # else:
            #     print('{}\t{}\t{}'.format(current_sysno, 'Schallplatte', 'ign'), file=sys.stderr)
            # if current_sysno in videokassette_sysnos:
            #     current_record, removed = filter_videokassette(current_record, out_videokassette_deleted,
            #                                                    out_videokassette_retained)
            #     print('{}\t{}\t{}'.format(current_sysno, 'Videokassette', 'del' if removed else 'ret'), file=sys.stderr)
            # else:
            #     print('{}\t{}\t{}'.format(current_sysno, 'Videokassette', 'ign'), file=sys.stderr)
            # if current_sysno in weltkarte_sysnos:
            #     current_record, removed = filter_weltkarte(current_record)
            #     print('{}\t{}\t{}'.format(current_sysno, 'Weltkarte', 'del' if removed else 'ret'), file=sys.stderr)
            # else:
            #     print('{}\t{}\t{}'.format(current_sysno, 'Weltkarte', 'ign'), file=sys.stderr)
            if current_sysno in zeitschrift_sysnos:
                current_record, removed = filter_zeitschrift(current_record, out_zeitschrift_deleted,
                                                             out_zeitschrift_retained)
                print('{}\t{}\t{}'.format(current_sysno, 'Zeitschrift', 'del' if removed else 'ret'), file=sys.stderr)
            else:
                print('{}\t{}\t{}'.format(current_sysno, 'Zeitschrift', 'ign'), file=sys.stderr)
            for l_out in current_record:
                print(l_out)
            current_sysno = line[0:9]
            current_record = [line]
    # if current_sysno in altkarte_sysnos:
    #     current_record, removed = filter_altkarte(current_record)
    #     print('{}\t{}\t{}'.format(current_sysno, 'Altkarte', 'del' if removed else 'ret'), file=sys.stderr)
    # else:
    #     print('{}\t{}\t{}'.format(current_sysno, 'Altkarte', 'ign'), file=sys.stderr)
    # if current_sysno in ausstellungskatalog_sysnos:
    #     current_record, removed = filter_ausstellungskatalog(current_record, cat_913,
    #                                                          out_ausstellungskatalog_deleted,
    #                                                          out_ausstellungskatalog_retained)
    #     if len(removed):
    #         for k, v in removed.items():
    #             if k == 'ALL':
    #                 print('{}\t{}\t{}'.format(current_sysno, 'Ausstellungskatalog', 'del'),
    #                       file=sys.stderr)
    #             else:
    #                 print('{}\t{}\t{}'.format(current_sysno, 'Ausstellungskatalog//' + k, 'del' if v else 'ret'),
    #                       file=sys.stderr)
    #     else:
    #         print('{}\t{}\t{}'.format(current_sysno, 'Ausstellungskatalog', 'ret'),
    #               file=sys.stderr)
    # else:
    #     print('{}\t{}\t{}'.format(current_sysno, 'Ausstellungskatalog', 'ign'), file=sys.stderr)
    # if current_sysno in briefsammlung_sysnos:
    #     current_record, removed = filter_briefsammlung(current_record, out_briefsammlung_deleted,
    #                                                    out_briefsammlung_retained)
    #     print('{}\t{}\t{}'.format(current_sysno, 'Briefsammlung', 'del' if removed else 'ret'), file=sys.stderr)
    # else:
    #     print('{}\t{}\t{}'.format(current_sysno, 'Briefsammlung', 'ign'), file=sys.stderr)
    if current_sysno in cd_sysnos:
        current_record, removed = filter_cd(current_record)
        print('{}\t{}\t{}'.format(current_sysno, 'CD', 'del' if removed else 'ret'), file=sys.stderr)
    else:
        print('{}\t{}\t{}'.format(current_sysno, 'CD', 'ign'), file=sys.stderr)
    if current_sysno in cdrom_sysnos:
        current_record, removed = filter_cdrom(current_record)
        print('{}\t{}\t{}'.format(current_sysno, 'CD-ROM', 'del' if removed else 'ret'), file=sys.stderr)
    else:
        print('{}\t{}\t{}'.format(current_sysno, 'CD-ROM', 'ign'), file=sys.stderr)
    # if current_sysno in comic_sysnos:
    #     current_record, removed = filter_comic(current_record, out_comic_deleted, out_comic_retained)
    #     print('{}\t{}\t{}'.format(current_sysno, 'Comic', 'del' if removed else 'ret'), file=sys.stderr)
    # else:
    #     print('{}\t{}\t{}'.format(current_sysno, 'Comic', 'ign'), file=sys.stderr)
    # if current_sysno in dvdrom_sysnos:
    #     current_record, removed = filter_dvdrom(current_record, out_dvdrom_deleted, out_dvdrom_retained)
    #     print('{}\t{}\t{}'.format(current_sysno, 'DVD-ROM', 'del' if removed else 'ret'), file=sys.stderr)
    # else:
    #     print('{}\t{}\t{}'.format(current_sysno, 'DVD-ROM', 'ign'), file=sys.stderr)
    # if current_sysno in dvdvideo_sysnos:
    #     current_record, removed = filter_dvdvideo(current_record, out_dvdvideo_deleted, out_dvdvideo_retained)
    #     print('{}\t{}\t{}'.format(current_sysno, 'DVD-Video', 'del' if removed else 'ret'), file=sys.stderr)
    # else:
    #     print('{}\t{}\t{}'.format(current_sysno, 'DVD-Video', 'ign'), file=sys.stderr)
    # if current_sysno in karte_sysnos:
    #     current_record, removed = filter_karte(current_record)
    #     print('{}\t{}\t{}'.format(current_sysno, 'Karte', 'del' if removed else 'ret'), file=sys.stderr)
    # else:
    #     print('{}\t{}\t{}'.format(current_sysno, 'Karte', 'ign'), file=sys.stderr)
    # if current_sysno in konferenzschrift_sysnos:
    #     current_record, removed = filter_konferenzschrift(current_record, cat_913, out_konferenzschrift_deleted,
    #                                                       out_konferenzschrift_retained)
    #     if len(removed):
    #         for k, v in removed.items():
    #             if k == 'ALL':
    #                 print('{}\t{}\t{}'.format(current_sysno, 'Konferenzschrift', 'del'),
    #                       file=sys.stderr)
    #             else:
    #                 print('{}\t{}\t{}'.format(current_sysno, 'Konferenzschrift//' + k, 'del' if v else 'ret'),
    #                       file=sys.stderr)
    #     else:
    #         print('{}\t{}\t{}'.format(current_sysno, 'Konferenzschrift', 'ret'),
    #               file=sys.stderr)
    # else:
    #     print('{}\t{}\t{}'.format(current_sysno, 'Konferenzschrift', 'ign'), file=sys.stderr)
    # if current_sysno in schallplatte_sysnos:
    #     current_record, removed = filter_schallplatte(current_record, out_schallplatte_deleted,
    #                                                   out_schallplatte_retained)
    #     print('{}\t{}\t{}'.format(current_sysno, 'Schallplatte', 'del' if removed else 'ret'), file=sys.stderr)
    # else:
    #     print('{}\t{}\t{}'.format(current_sysno, 'Schallplatte', 'ign'), file=sys.stderr)
    # if current_sysno in videokassette_sysnos:
    #     current_record, removed = filter_videokassette(current_record, out_videokassette_deleted,
    #                                                    out_videokassette_retained)
    #     print('{}\t{}\t{}'.format(current_sysno, 'Videokassette', 'del' if removed else 'ret'), file=sys.stderr)
    # if current_sysno in weltkarte_sysnos:
    #     current_record, removed = filter_weltkarte(current_record)
    #     print('{}\t{}\t{}'.format(current_sysno, 'Weltkarte', 'del' if removed else 'ret'), file=sys.stderr)
    # else:
    #     print('{}\t{}\t{}'.format(current_sysno, 'Weltkarte', 'ign'), file=sys.stderr)
    if current_sysno in zeitschrift_sysnos:
        current_record, removed = filter_zeitschrift(current_record, out_zeitschrift_deleted, out_zeitschrift_retained)
        print('{}\t{}\t{}'.format(current_sysno, 'Zeitschrift', 'del' if removed else 'ret'), file=sys.stderr)
    else:
        print('{}\t{}\t{}'.format(current_sysno, 'Zeitschrift', 'ign'), file=sys.stderr)
    for l_out in current_record:
        print(l_out)

    # out_ausstellungskatalog_deleted.close()
    # out_ausstellungskatalog_retained.close()
    # out_briefsammlung_deleted.close()
    # out_briefsammlung_retained.close()
    # out_comic_deleted.close()
    # out_comic_retained.close()
    # out_dvdrom_deleted.close()
    # out_dvdrom_retained.close()
    # out_dvdvideo_deleted.close()
    # out_dvdvideo_retained.close()
    # out_konferenzschrift_deleted.close()
    # out_konferenzschrift_retained.close()
    # out_schallplatte_deleted.close()
    # out_schallplatte_retained.close()
    # out_videokassette_deleted.close()
    # out_videokassette_retained.close()
    out_zeitschrift_deleted.close()
    out_zeitschrift_retained.close()
