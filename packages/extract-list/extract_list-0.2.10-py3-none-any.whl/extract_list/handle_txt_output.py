#! /usr/local/bin/python3
"""Print list of dicts as table in text."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from typing import TextIO
from extract_list.commontypes import Value, Data
from extract_list.extract_config import ExtractConfig


def print_col(file: TextIO, item: Value, width: int) -> None:
    """Print a single column item to file with width."""
    txt = str(item)
    txt += ' '*(width-len(txt))
    file.write(txt)


def txt_output(data: Data, column_order: list[str],
               filename: str, encoding: str) -> None:
    """Print list of dicts as table in text."""
    column_width: dict[str, int] = {k: len(k)+1 for k in column_order}
    for row in data:
        for col in column_order:
            if column_width[col] <= len(str(row[col])) + 1:
                column_width[col] = len(str(row[col])) + 1
    with open(file=filename, mode='w', encoding=encoding) as file:
        for key, width in column_width.items():
            print_col(file=file, item=key, width=width)
        file.write('\n')
        for row in data:
            for key, width in column_width.items():
                print_col(file=file, item=row[key], width=width)
            file.write('\n')


def handle_txt_output(data: Data, filename: str, cfg: ExtractConfig) -> None:
    """Handle output to text file."""
    txt_output(data=data, column_order=cfg.column_order, filename=filename,
               encoding=cfg.outfile_encoding)
