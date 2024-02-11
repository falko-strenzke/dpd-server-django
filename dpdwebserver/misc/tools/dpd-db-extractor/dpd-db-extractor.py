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


def update_all_construction(source_conn : sqlite3.Connection, target_conn : sqlite3.Connection,
                            limit_cnt : int = 0 ):
    t = Terminal()
    t.green("updating construction elements")
    target_cur = target_conn.cursor()
    target_cur.execute("DELETE from dict_construction_element")
    target_cur.execute("SELECT headword FROM dict_headword")
    source_cur = source_conn.cursor()
    loop_cnt : int = 0
    for target_row in target_cur:
        loop_cnt += 1
        if limit_cnt > 0 and loop_cnt > limit_cnt:
            t.yellow(f"reached configured limit of {limit_cnt}, stopping.")
            break
        headword : str = target_row[0]
        #print(f'"{headword}"')
        #if headword.find('"') != -1:
        #    t.yellow("skipping this entry")
        #    continue
        source_cur.execute("SELECT construction FROM pali_words WHERE pali_1=?", (headword,))
        source_rows = source_cur.fetchall()
        if len(source_rows) == 0:
            print(t.red("missing entry for headword '" + headword + "' in source_db"))
            continue
        if len(source_rows) > 1:
            print(t.red("found multiple (" + str(len(source_rows)) + ") entries for headword '" + headword + "' in source_db"))
        construction_elements_line = source_rows[0]
        constr_elems = construction_elements_line.split("+")
        root_found = False
        prefix_ctr = 1
        suffix_ctr = -1

        class ElemData:
            def __init__(self, headword, text, prefix_ctr, suffix_ctr):
                self.headword = headword
                self.text = text
                self.prefix_ctr = prefix_ctr
                self.suffix_ctr = suffix_ctr
        elem_data_list : list[ElemData] = []
        prefix_ctr_before_root : Optional[int] = None
        for elem in constr_elems:
            if prefix_ctr == 0:
                # previous element was a root
                prefix_ctr = -1
                suffix_ctr = len(constr_elems) - prefix_ctr_before_root
            if elem.find("√") != -1:
                prefix_ctr_before_root = prefix_ctr
                prefix_ctr = 0
                root_found = True
            data = ElemData(headword, elem.trim(), prefix_ctr, suffix_ctr)
            elem_data_list.append(data)
            if not root_found:
                prefix_ctr += 1
            else:
                suffix_ctr -= 1
        if not root_found:
            # if no root was found, need create the counting of the suffixes from rear:
            suffix_ctr = 1
            for i in reversed(range(0, len(elem_data_list) - 1)):
                elem_data_list[i].suffix_ctr = suffix_ctr
                suffix_ctr += 1
        # write the data elements into the DB:
        for data in elem_data_list:
            target_conn.execute("INSERT INTO dict_construction_element (headword, text, prefix_pos, suffix_pos) VALUES (?, ?, ?, ?)", (data.headword, data.text, data.prefix_ctr, data.suffix_ctr,))
    target_conn.commit()





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
    update_all_construction(source_conn=source_conn, target_conn=target_conn)


if __name__ == "__main__":
    main()
