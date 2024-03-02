#!/usr/bin/python3
import argparse
import sys
import os
import os.path
import sqlite3
import re
from configparser import ConfigParser
import json
import click
from blessings import Terminal
from typing import Optional

DEFAULT_CFG = "config.ini"

def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def update_all_construction(source_conn : sqlite3.Connection, target_conn : sqlite3.Connection,
                            limit_cnt : int = 0 ):
    t = Terminal()
    t.green("updating construction elements")
    target_cur = target_conn.cursor()
    target_cur.execute("DELETE from dict_construction_element")
    target_cur.execute("DELETE from dict_construction_element_set")
    target_cur.execute("SELECT pali_1 FROM dict_pali_word")
    source_cur = source_conn.cursor()
    constr_elem_set : set[str] = set()
    loop_cnt : int = 0
    for target_row in target_cur:
        print(t.blue(f"starting loop with loop_cnt = {loop_cnt}"))
        if limit_cnt > 0 and loop_cnt > limit_cnt:
            print(t.yellow(f"reached configured limit of {limit_cnt}, stopping."))
            break
        else:
            print(t.blue(f"limit of {limit_cnt} not yet reached"))
        headword : str = target_row[0]
        #print(f'"{headword}"')
        #if headword.find('"') != -1:
        #    t.yellow("skipping this entry")
        #    continue
        source_cur.execute("SELECT construction, compound_type, grammar FROM pali_words WHERE pali_1=?", (headword,))
        source_rows = source_cur.fetchall()
        if len(source_rows) == 0:
            print(t.red("missing entry for headword '" + headword + "' in source_db"))
            continue
        if len(source_rows) > 1:
            print(t.red("found multiple (" + str(len(source_rows)) + ") entries for headword '" + headword + "' in source_db, aborting"))
            sys.exit(1)
        loop_cnt += 1
        construction_elements_line = source_rows[0][0]
        compound_type = source_rows[0][1]
        grammar : str = source_rows[0][2]
        is_compound = True if compound_type != "" or grammar.find("comp") != -1 else False
        print(construction_elements_line)
        if construction_elements_line == "":
            continue
        # ignore everything beyond the first line
        constructions_elements_line_splitted = construction_elements_line.split('\n')
        construction_elements_line = constructions_elements_line_splitted[0]
        constr_elems = construction_elements_line.split("+")
        root_found = False
        prefix_ctr = 1
        suffix_ctr = -1

        class ElemData:

            def full_element_text_to_original_token_and_phonetic_change(self, text : str) -> tuple[str, str]:
                tokens = text.split(">")
                if len(tokens) > 1:
                    return (tokens[0], text)
                return (text, "")

            def __init__(self, headword, text, prefix_ctr, suffix_ctr):
                original_token__phonetic_change = self.full_element_text_to_original_token_and_phonetic_change(text)
                self.headword = headword
                self.text = original_token__phonetic_change[0]
                self.phonetic_change = original_token__phonetic_change[1]
                self.prefix_ctr = prefix_ctr
                self.suffix_ctr = suffix_ctr

            def has_phonetic_change(self) -> bool:
                return self.phonetic_change != ""

        elem_data_list : list[ElemData] = []
        prefix_ctr_before_root : Optional[int] = None
        for elem in constr_elems:
            elem = elem.strip()
            if prefix_ctr == 0:
                # previous element was a root
                prefix_ctr = -1
                suffix_ctr = len(constr_elems) - prefix_ctr_before_root
            if elem.find("√") != -1:
                prefix_ctr_before_root = prefix_ctr
                prefix_ctr = 0
                root_found = True
            data = ElemData(headword, elem, prefix_ctr, suffix_ctr)
            if not is_compound:
                constr_elem_set.add(data.text)
            elem_data_list.append(data)
            if not root_found:
                prefix_ctr += 1
            else:
                suffix_ctr -= 1
        if not root_found:
            # if no root was found, need create the counting of the suffixes from rear:
            suffix_ctr = 1
            for i in reversed(range(0, len(elem_data_list))):
                data = elem_data_list[i]
                data.suffix_ctr = suffix_ctr
                print(t.blue(f"{data.headword}: assigned suffix_ctr = {suffix_ctr} to element number {i}"))
                suffix_ctr += 1
        # write the data elements into the DB:
        for data in elem_data_list:
            print(t.blue("going to insert regular element into db"))
            target_conn.execute("INSERT INTO dict_construction_element (headword_id, text, prefix_pos, suffix_pos, is_phonetic_change) VALUES (?, ?, ?, ?, ?)", (data.headword, data.text, data.prefix_ctr, data.suffix_ctr, False,))
            if data.has_phonetic_change():
                # set an additional entry for the phonetic change
                print(t.blue("going to insert phonetic_change into db"))
                target_conn.execute("INSERT INTO dict_construction_element (headword_id, text, prefix_pos, suffix_pos, is_phonetic_change) VALUES (?, ?, ?, ?, ?)", (data.headword, data.phonetic_change, data.prefix_ctr, data.suffix_ctr, True))
        # dict_headword is DEPRECATED. Not needed, column "construction" is already present (with multiple lines, though)
        #target_conn.execute("UPDATE dict_headword SET construction_text = ? WHERE headword=?", (construction_elements_line, headword,) )
        print(t.blue(f"update for headword {headword} complete"))
    print(t.blue("committing the changes to db"))
    for constr_elem_in_set in constr_elem_set:
        max_len = 255
        if not constr_elem_in_set.startswith("√") and len(constr_elem_in_set) > max_len:
            continue
        target_conn.execute("INSERT INTO dict_construction_element_set (text) VALUES (?)", (constr_elem_in_set,))


def copy_table(source_conn : sqlite3.Connection, target_conn : sqlite3.Connection, source_table_name : str, target_table_name : str, columns : list[str]) -> None:
    target_cur = target_conn.cursor()
    target_cur.execute("DELETE from " + target_table_name)
    source_cur = source_conn.cursor()
    source_cur.execute("SELECT " + ", ".join(columns) + " FROM " + source_table_name)
    source_rows = source_cur.fetchall()
    #update_SET : str = ""
    #for column in columns:
    #    update_SET += ", " if update_SET != "" else ""
    #    update_SET + column + "=?"
    i = 0
    for source_row in source_rows:
        printProgressBar(i, len(source_rows), prefix=source_table_name + ':', suffix='Complete', length=50)
        i = i + 1
        source_row_quoted = ['"' + str(el) + '"' for el in source_row]
        insert_cmd : str = "INSERT INTO " + target_table_name + " (" + ", ".join(columns) + ") VALUES( " + ", ".join(source_row_quoted) + ")"
        #print(insert_cmd)
        target_cur.execute(insert_cmd)


def copy_pali_words_table(source_conn : sqlite3.Connection, target_conn : sqlite3.Connection):
    cols_to_copy = [
        'pali_1',
        'pali_2',
        'pos',
        'grammar',
        'derived_from',
        'verb',
        'trans',
        'plus_case',
        'meaning_1',
        'meaning_2',
        'meaning_lit',
        'sanskrit',
        'root_key',
        'root_sign',
        'root_base',
        'construction',
        'derivative',
        'suffix',
        'phonetic',
        'compound_type',
        'compound_construction',
        'non_root_in_comps',
        'synonym',
        'variant',
        'stem',
        'pattern',
    ]
    copy_table(source_conn, target_conn, "pali_words", "dict_pali_word", cols_to_copy)



def copy_pali_roots_table(source_conn : sqlite3.Connection, target_conn : sqlite3.Connection) -> None:
    cols_to_copy = [
        'root',
        'root_in_comps',
        #'root_has_verb', TODO: FILL AS BOOLEAN
        'root_group',
        'root_sign',
        'root_meaning',
        'sanskrit_root',
        'sanskrit_root_meaning',
        'sanskrit_root_class',
        'root_example',
        'dhatupatha_num',
        'dhatupatha_root',
        'dhatupatha_pali',
        'dhatupatha_english',
        'dhatumanjusa_num',
        'dhatumanjusa_root',
        'dhatumanjusa_pali',
        'dhatumanjusa_english',
        'dhatumala_root',
        'dhatumala_pali',
        'dhatumala_english',
        'panini_root',
        'panini_sanskrit',
        'panini_english',
        'note',
        'matrix_test',
        'root_info',
        'root_matrix'
    ]
    copy_table(source_conn, target_conn, "pali_roots", "dict_pali_root", cols_to_copy)



def copy_inflection_to_headwords_table(source_conn : sqlite3.Connection, target_conn : sqlite3.Connection):
    cols_to_copy = [
        'inflection',
        'headwords'
    ]
    copy_table(source_conn, target_conn, "inflection_to_headwords", "dict_inflection_to_headwords", cols_to_copy)


def copy_sandhi_table(source_conn : sqlite3.Connection, target_conn : sqlite3.Connection):
    cols_to_copy = [
        'sandhi',
        'split'
    ]
    copy_table(source_conn, target_conn, "sandhi", "dict_sandhi", cols_to_copy)



def copy_tables_from_dpd_db(source_conn : sqlite3.Connection, target_conn : sqlite3.Connection) -> None:
    copy_pali_words_table(source_conn, target_conn)
    copy_pali_roots_table(source_conn, target_conn)
    copy_inflection_to_headwords_table(source_conn, target_conn)
    copy_sandhi_table(source_conn, target_conn)


def configure(ctx, param, filename):
    cfg = ConfigParser()
    cfg.read(filename)
    try:
        options = dict(cfg["options"])
    except KeyError:
        options = {}
    ctx.default_map = options


@click.command()
@click.option(
    "-c",
    "--config",
    type=click.Path(dir_okay=False),
    default=DEFAULT_CFG,
    callback=configure,
    is_eager=True,
    expose_value=False,
    help="Read option defaults from the specified INI file",
    show_default=True,
)
@click.option("--target-db", type=click.Path(exists=True))
@click.option("--source-db", type=click.Path(exists=True))
@click.option("--limit", default=0)
#click.option("--choice", type=click.Choice(["red", "green", "blue"]))
def main(target_db : str, source_db : str, limit : int):
    term = Terminal()
    if source_db is None or source_db == "":
       term.red("must provide configuration option for source-db")
       exit(1)
    if target_db is None or source_db == "":
       term.red("must provide configuration option for target-db")
       exit(1)
    source_conn : sqlite3.Connection = sqlite3.connect(source_db)
    target_conn : sqlite3.Connection = sqlite3.connect(target_db)

    copy_tables_from_dpd_db(source_conn, target_conn)
    update_all_construction(source_conn=source_conn, target_conn=target_conn, limit_cnt=limit)
    target_conn.commit()




if __name__ == "__main__":
    main()
