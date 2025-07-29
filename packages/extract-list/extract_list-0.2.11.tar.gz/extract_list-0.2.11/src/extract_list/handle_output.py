#! /usr/local/bin/python3
"""Produce output to file in chosen format."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License


from excel_list_transform.file_extension import fix_file_extension
from excel_list_transform.handle_csv import write_csv_named
from excel_list_transform.handle_excel import write_excel_named
from extract_list.extract_config import ExtractConfig
from extract_list.commontypes import Data
from extract_list.config_enums import OutFileType
from extract_list.handle_json_xml_output import \
    handle_json_output, handle_xml_output
from extract_list.handle_txt_output import handle_txt_output


def handle_csv_output(data: Data, filename: str, cfg: ExtractConfig) -> None:
    """Handle output to CSV file."""
    write_csv_named(data=data, filename=filename,
                    dialect=cfg.get_out_csv_dialect(),
                    encoding=cfg.outfile_encoding,
                    column_order=cfg.column_order)


def handle_excel_output(data: Data, filename: str,
                        cfg: ExtractConfig) -> None:
    """Handle output to excel file."""
    write_excel_named(data=data, filename=filename,
                      column_order=cfg.column_order,
                      excel_lib=cfg.outfile_excel_library)


FILE_EXTESION = {
    OutFileType.CSV: '.csv',
    OutFileType.EXCEL: '.xlsx',
    OutFileType.JSON: '.json',
    OutFileType.TXT: '.txt',
    OutFileType.XML: '.xml'
}

OUT_DISPATCH = {
    OutFileType.CSV: handle_csv_output,
    OutFileType.EXCEL: handle_excel_output,
    OutFileType.JSON: handle_json_output,
    OutFileType.TXT: handle_txt_output,
    OutFileType.XML: handle_xml_output
}


def handle_output(data: Data, filename: str, cfg: ExtractConfig) -> None:
    """Write out data to file in correct format."""
    extension = FILE_EXTESION[cfg.outfile_type]
    fixed_fname = fix_file_extension(filename=filename, ext_to_add=extension)
    OUT_DISPATCH[cfg.outfile_type](data=data, filename=fixed_fname, cfg=cfg)
