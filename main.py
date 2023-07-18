#!/usr/bin/env -S python3

import argparse
import csv
from dataclasses import dataclass
from typing import Union
from abc import ABC


QueryNode = Union['MatchOperator', 'AndOperator', 'OrOperator', None]

@dataclass
class MatchOperator:
    column_name: str
    matching_value: str

@dataclass
class UnaryBoolean(ABC):
    v1: QueryNode

@dataclass
class BinaryBoolean(ABC):
    v1: QueryNode
    v2: QueryNode

@dataclass
class NotOperator(UnaryBoolean):
    pass

@dataclass
class AndOperator(BinaryBoolean):
    pass

@dataclass
class OrOperator(BinaryBoolean):
    pass


@dataclass
class Row:
    raw: str
    row_dict: dict


def parse_match_args(args: str) -> MatchOperator | None:
    match_args = args.strip(")").split(",")
    if len(match_args) != 2:
        return None
    return MatchOperator(
        column_name=match_args[0].strip('" '), matching_value=match_args[1].strip('" '))


def parse_unary_args(op_type: UnaryBoolean, body: str) -> UnaryBoolean | None:
    return op_type(parse_query(body))


def parse_query(search_query: str) -> QueryNode:
    tree = None
    match search_query.partition("("):
        case op, "(", body:
            if body[-1] != ")":
                return None
            match op:
                case "MATCH":
                    return parse_match_args(body[:-1])
                case "NOT":
                    return parse_unary_args(NotOperator, body)
                case "AND" | "OR":
                    return AndOperator(None, None)
                case "OR":
                    return OrOperator(None, None)
                case _:
                    return None
        case _:
            return None

    return tree

    
def eval_search_query(row: Row, search_query: QueryNode) -> bool:
    if isinstance(search_query, MatchOperator):
        matcher: MatchOperator = search_query
        return matcher.column_name in row.row_dict \
            and row.row_dict[matcher.column_name] == matcher.matching_value
    elif isinstance(search_query, NotOperator):
        return not(eval_search_query(row, search_query.v1)) 
    elif isinstance(search_query, AndOperator):
        return eval_search_query(row, search_query.v1) and eval_search_query(row, search_query.v2)
    elif isinstance(search_query, OrOperator):
        return eval_search_query(row, search_query.v1) or eval_search_query(row, search_query.v2)
    else:
        print(f"Warning: eval_search_query support not implemented QueryNode type. QueryNode: {type(search_query)}")
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