#! /usr/local/bin/python3
"""Generate example configuration for extracting a list from JSON or XML."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

# from typing import TextIO
from enum import Enum
from excel_list_transform.str_to_enum import string_to_enum_best_match
from excel_list_transform.file_extension import fix_file_extension
from extract_list.config_enums import OutFileType, InFileType, \
    MissingInputForColumn
from extract_list.extract_config import ExtractConfig, \
    MLineDict, MainLineSpec, LLineDict, LinkedLineSpec
from extract_list.commontypes import CfgTypes
from extract_list.generate_txt_sw_to_rrs import generate_txt_sw_to_rrs
from extract_list.generate_txt_example_json import \
    generate_txt_example_json, generate_txt_example2_json
from extract_list.generate_txt_example_xml import \
    generate_txt_example_xml, generate_txt_example2_xml


def generate_cfg_example(outfilename: str, cfgtype: CfgTypes,
                         outtype: OutFileType) -> int:
    """Generate cfg file for example."""
    assert cfgtype in (CfgTypes.EXAMPLE_JSON, CfgTypes.EXAMPLE_XML)
    cfg = ExtractConfig()
    cfg.outfile_type = outtype
    if cfgtype == CfgTypes.EXAMPLE_JSON:
        cfg.infile_type = InFileType.JSON
    else:  # XML
        cfg.infile_type = InFileType.XML
        cfg.main_line.line.insert(0, 'data')
        cfg.linked_lines[0].line.insert(0, 'data')
    cfg.write(to_json_filename=outfilename)
    return 0


def generate_cfg_example2(outfilename: str, cfgtype: CfgTypes,
                          outtype: OutFileType) -> int:
    """Generate cfg file for example."""
    assert cfgtype in (CfgTypes.EXAMPLE2_JSON, CfgTypes.EXAMPLE2_XML)
    cfg = ExtractConfig()
    main_col = {'Customer name': ['name'],
                'Street': ['address', 'street'],
                'Street number': ['address', 'number']}
    mline: MLineDict = {'line': ['customers'], 'columns': main_col,
                        'expand_at': []}
    cfg.main_line = MainLineSpec(data=mline)
    l1col = {'What': ['items', 'item'],
             'How many': ['items', 'quantity']}
    l1line: LLineDict = {'line': ['orders'], 'columns': l1col,
                         'linked_column': ['customer'],
                         'linked_main_column': ['customer_number'],
                         'expand_at':  [['items']]}
    l2col = {'Deliver by': ['deliver_by']}
    l2line: LLineDict = {'line': ['delivery_method'], 'columns': l2col,
                         'linked_column': ['for_street'],
                         'linked_main_column': ['address', 'street'],
                         'expand_at':  []}
    cfg.linked_lines = [LinkedLineSpec(data=l1line),
                        LinkedLineSpec(data=l2line)]
    cfg.outfile_type = outtype
    cfg.one_output_line_per_main_line = False
    cfg.column_order = ['What', 'How many', 'Customer name',
                        'Street', 'Street number', 'Deliver by']
    cfg.include_key = False
    cfg.missing_input_for_column = MissingInputForColumn.ERROR
    if cfgtype == CfgTypes.EXAMPLE2_JSON:
        cfg.infile_type = InFileType.JSON
    else:  # XML
        cfg.infile_type = InFileType.XML
        cfg.main_line.line.insert(0, 'data')
        cfg.linked_lines[0].line.insert(0, 'data')
        cfg.linked_lines[1].line.insert(0, 'data')
    cfg.write(to_json_filename=outfilename)
    return 0


def generate_cfg_sw_to_rrs(outfilename: str, cfgtype: CfgTypes,
                           outtype: OutFileType) -> int:
    """Generate cfg file for SailWave to RRS."""
    assert cfgtype in (CfgTypes.SW_JSON_TO_RRS, CfgTypes.SW_XML_TO_RRS)
    cfg = ExtractConfig()
    cfg.infile_encoding = 'cp1252'
    cfg.outfile_type = outtype
    cfg.linked_lines = []
    cfg.main_line.line = ['competitors']
    cfg.main_line.expand_at = []
    cfg.main_line.columns = {'Class': ['compclass'],
                             'Division': ['compdivision'],
                             'Nationality': ['compnat'],
                             'Sail Number': ['compsailno'],
                             'Boat Name': ['compboat'],
                             'Name': ['comphelmname'],
                             'Club Name': ['compclub'],
                             'Email': ['comphelmemail'],
                             'Phone': ['comphelmphone']}
    cfg.include_key = False
    cfg.column_order = ['Class', 'Division', 'Nationality', 'Sail Number',
                        'Boat Name', 'Name', 'Club Name', 'Email', 'Phone']
    cfg.missing_input_for_column = MissingInputForColumn.EMPTY
    cfg.out_xml_attributes = []
    if cfgtype == CfgTypes.SW_JSON_TO_RRS:
        cfg.infile_type = InFileType.JSON
    else:  # XML
        cfg.infile_type = InFileType.XML
        cfg.main_line.line.insert(0, 'sailwave-data')
        cfg.main_line.line.append('competitor')
    cfg.write(to_json_filename=outfilename)
    return 0


def _lower_str_enum(etype: type[Enum]) -> list[str]:
    """Get a lower case list of strings for enum."""
    return [e.name.lower() for e in etype]


def get_types_of_cfg() -> list[str]:
    """Get a list of possible example configurations."""
    return _lower_str_enum(CfgTypes)


def get_out_file_types() -> list[str]:
    """Get a list of possible out file types in config."""
    return _lower_str_enum(OutFileType)


TXTFUNCS = {CfgTypes.EXAMPLE_JSON: generate_txt_example_json,
            CfgTypes.EXAMPLE_XML: generate_txt_example_xml,
            CfgTypes.EXAMPLE2_JSON: generate_txt_example2_json,
            CfgTypes.EXAMPLE2_XML: generate_txt_example2_xml,
            CfgTypes.SW_JSON_TO_RRS: generate_txt_sw_to_rrs,
            CfgTypes.SW_XML_TO_RRS: generate_txt_sw_to_rrs}

CFGFUNCS = {CfgTypes.EXAMPLE_JSON: generate_cfg_example,
            CfgTypes.EXAMPLE_XML: generate_cfg_example,
            CfgTypes.EXAMPLE2_JSON: generate_cfg_example2,
            CfgTypes.EXAMPLE2_XML: generate_cfg_example2,
            CfgTypes.SW_JSON_TO_RRS: generate_cfg_sw_to_rrs,
            CfgTypes.SW_XML_TO_RRS: generate_cfg_sw_to_rrs}


def generate_example_cfg(filename: str, cfgtype: str,
                         out_file_type: str) -> int:
    """Generate example configuration file and accompanying txt file."""
    type_of_cfg = string_to_enum_best_match(inp=cfgtype, num_type=CfgTypes)
    type_out = string_to_enum_best_match(inp=out_file_type,
                                         num_type=OutFileType)
    cfgout = fix_file_extension(filename=filename, ext_to_add='.cfg')
    ret = CFGFUNCS[type_of_cfg](outfilename=cfgout, cfgtype=type_of_cfg,
                                outtype=type_out)
    if ret != 0:  # pragma: no cover
        return ret
    txtout = fix_file_extension(filename=filename, ext_to_add='.txt',
                                ext_to_remove='.cfg')
    with open(file=txtout, mode='wt', encoding='utf-8') as file:
        ret = TXTFUNCS[type_of_cfg](file=file, cfgtype=type_of_cfg,
                                    outtype=type_out)
        return ret
