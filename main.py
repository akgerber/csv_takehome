#!/usr/bin/env -S python3

import argparse
import csv
from dataclasses import dataclass

@dataclass
class MatchOperator:
    column_name: str
    matching_value: str


QueryNode = MatchOperator | None

@dataclass
class ParsedQuery:
    tree: QueryNode


@dataclass
class Row:
    raw: str
    row_dict: dict


def parse_match_args(args: str) -> MatchOperator | None:
    match_args = args.strip(")").split(",")
    if len(match_args) != 2:
        return False
    return MatchOperator(
        column_name=match_args[0].strip('" '), matching_value=match_args[1].strip('" '))


def parse_query(search_query: str) -> ParsedQuery | None:
    tree = None
    match search_query.split("("):
        case "MATCH", body:
            if body[-1] != ")":
                return None
            match = parse_match_args(body[:-1])
            if match is None:
                return None
            tree = match
        case _:
            return None

    return ParsedQuery(tree=tree)

    
def eval_search_query(row: Row, search_query: ParsedQuery) -> bool:
    if type(search_query.tree) == MatchOperator:
        matcher: MatchOperator = search_query.tree
        return matcher.column_name in row.row_dict \
            and row.row_dict[matcher.column_name] == matcher.matching_value
    else:
        return False
    

def main(csv_filename: str, search_query: str) -> bool:
    query = parse_query(search_query)
    if query is None:
        print(f"Cannot parse query: {search_query}")
        return False

    try: 
        with open(csv_filename, newline='') as f:
            dict_reader = csv.DictReader(f)
            rows_dicts = [row for row in dict_reader]
        with open(csv_filename, newline='') as f:
            next(f) # skip header row
            rows_raw = [row.strip() for row in f]
    except FileNotFoundError:
        print(f"File does not exist: {csv_filename}")
        return False

    row_data = (Row(raw=raw, row_dict=row_dict) 
                for (raw, row_dict) in zip(rows_raw, rows_dicts))

    for row in row_data:
        if eval_search_query(row, query):
            print(row.raw)

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="CSV Searcher"
    )

    parser.add_argument('filename')
    parser.add_argument('search_query')
    args = parser.parse_args()

    main(csv_filename=args.filename, search_query=args.search_query)