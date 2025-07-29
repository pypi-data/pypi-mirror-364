#! /usr/local/bin/python3
"""Function for handling data extraction with files."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from excel_list_transform.file_extension import fix_file_extension
from excel_list_transform.file_must_exist import file_must_exist
from extract_list.extract_data import extract_data
from extract_list.handle_input import handle_input
from extract_list.handle_output import handle_output
from extract_list.extract_config import ExtractConfig


def extract_func(in_file_name: str, cfg_file_name: str,
                 out_file_name: str) -> int:
    """Extract data from in file, write to out_file."""
    fixed_cfg = fix_file_extension(filename=cfg_file_name,
                                   ext_to_add='.cfg', ext_to_remove=None,
                                   for_reading=True)
    file_must_exist(filename=fixed_cfg, with_content_txt='configuration')
    cfg = ExtractConfig(from_json_filename=fixed_cfg)
    indata = handle_input(filename=in_file_name, cfg=cfg)
    outdata = extract_data(indata=indata, cfg=cfg)
    handle_output(data=outdata, filename=out_file_name, cfg=cfg)
    return 0
