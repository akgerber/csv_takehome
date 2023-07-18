#!/usr/bin/env -S python3

import argparse

def main(csv_filename: str, search_query: str):
    print(csv_filename)
    print(search_query)

    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="CSV Searcher"
    )

    parser.add_argument('filename')
    parser.add_argument('search_query')
    args = parser.parse_args()

    main(csv_filename=args.filename, search_query=args.search_query)