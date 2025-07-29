#! /usr/local/bin/python3
"""Read input from file in chosen format."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from typing import OrderedDict, cast, Mapping, Any
import json
import xmltodict
from excel_list_transform.file_extension import fix_file_extension
from excel_list_transform.file_must_exist import file_must_exist
from excel_list_transform.commontypes import JsonType
from extract_list.extract_config import ExtractConfig
from extract_list.config_enums import InFileType


def read_in_json(filename: str, encoding: str) -> JsonType:
    """Read data from JSON file."""
    with open(file=filename, mode='r', encoding=encoding) as file:
        data = json.load(fp=file)
    return cast(JsonType, data)


def handle_json_input(filename: str, cfg: ExtractConfig) -> JsonType:
    """Handle input of data from JDON file."""
    return read_in_json(filename=filename, encoding=cfg.infile_encoding)


def strip_prefix_dict(indata: Mapping[str, Any] | JsonType,
                      prefix: str) -> JsonType:
    """Strip prefix from all keys in dicts recursively."""
    if isinstance(indata, (dict, OrderedDict)):
        dres: dict[str, JsonType] = {}
        for key, value in indata.items():
            newkey = key.removeprefix(prefix)
            dres[newkey] = strip_prefix_dict(indata=value, prefix=prefix)
        return dres
    if isinstance(indata, list):
        ares: list[JsonType] = []
        for value in indata:
            ares.append(strip_prefix_dict(indata=value, prefix=prefix))
        return ares
    return cast(JsonType, indata)


def read_in_xml(filename: str, encoding: str,
                strip_at: bool) -> JsonType:
    """Read data from XML file."""
    with open(file=filename, mode='r', encoding=encoding) as file:
        txt = file.read()
        data = xmltodict.parse(xml_input=txt)
    if strip_at:
        return strip_prefix_dict(indata=data, prefix='@')
    return cast(JsonType, data)


def handle_xml_input(filename: str, cfg: ExtractConfig) -> JsonType:
    """Handle input of data from XML§ file."""
    return read_in_xml(filename=filename, encoding=cfg.infile_encoding,
                       strip_at=cfg.in_xml_strip_at)


FILE_EXTESION = {
    InFileType.JSON: '.json',
    InFileType.XML: '.xml'
}

IN_DISPATCH = {
    InFileType.JSON: handle_json_input,
    InFileType.XML: handle_xml_input
}


def handle_input(filename: str, cfg: ExtractConfig) -> JsonType:
    """Read in data from file parsing correct format."""
    extension = FILE_EXTESION[cfg.infile_type]
    fixed_fname = fix_file_extension(filename=filename, ext_to_add=extension,
                                     for_reading=True)
    file_must_exist(filename=fixed_fname)
    return IN_DISPATCH[cfg.infile_type](filename=fixed_fname, cfg=cfg)
