#! /usr/local/bin/python3
"""Print list of dicts as JSON or XML."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from copy import deepcopy
import json
import xmltodict
from excel_list_transform.commontypes import get_checked_type
from extract_list.commontypes import Data, Row, Value
from extract_list.extract_config import ExtractConfig


def json_output(data: Data, filename: str, encoding: str) -> None:
    """Print list of dicts to JSON."""
    with open(file=filename, mode='w', encoding=encoding) as file:
        json.dump(data, fp=file, indent=2)


def append_to_key(row: Row, key: str, prefix: str) -> None:
    """Add prefix to key in dict row."""
    value: Value = row.pop(key)
    row[prefix + key] = value


def handle_xml_output(data: Data, filename: str, cfg: ExtractConfig) -> None:
    """Handle output to XML file."""
    indata = deepcopy(data)
    outdata: dict[str, dict[str, Value]] = {}
    for i, row in enumerate(indata):
        for key in cfg.out_xml_attributes:
            append_to_key(row=row, key=key, prefix='@')
        rowkey = 'row_' + str(i)
        if cfg.include_key and cfg.column_name_for_key in row:
            rowkey = get_checked_type(row[cfg.column_name_for_key], str)
        outdata[rowkey] = row
    to_output = {'data': outdata}
    with open(file=filename, mode='w', encoding=cfg.outfile_encoding) as file:
        xmltodict.unparse(to_output, output=file, pretty=True,
                          encoding=cfg.outfile_encoding)


def handle_json_output(data: Data, filename: str, cfg: ExtractConfig) -> None:
    """Handle output to JSON file."""
    json_output(data=data, filename=filename, encoding=cfg.outfile_encoding)
