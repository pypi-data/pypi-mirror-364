#! /usr/local/bin/python3
"""Generate text describing example configuration."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from typing import TextIO
import sys
from extract_list.config_enums import OutFileType
from extract_list.commontypes import CfgTypes
from extract_list.generate_txt_syntax import generate_syntax_txt


def generate_txt_sw_to_rrs(file: TextIO, cfgtype: CfgTypes,
                           outtype: OutFileType) -> int:
    """Write text describing configuration example_json."""
    assert cfgtype in (CfgTypes.SW_JSON_TO_RRS, CfgTypes.SW_XML_TO_RRS)
    if outtype not in (OutFileType.CSV, OutFileType.EXCEL):
        noticemsg = '\nNotice: The expected next step excel-list-transform\n'
        noticemsg += '        will require input in excel or CSV format!\n'
        noticemsg += '        But the selected output type is: '
        noticemsg += outtype.name
        noticemsg += '!\n\n'
        print(noticemsg, file=sys.stderr)
        print(noticemsg, file=file)
    path = '"competitors"'
    msg = '''
    This is an example created to show how data exported from
    https://www.sailwave.com (SW) as '''
    if cfgtype == CfgTypes.SW_JSON_TO_RRS:
        msg += 'JSON data'
    else:
        msg += 'XML data'
        path = '["sailwave-data", "competitors", "competitor"]'
    msg += f'''
    can be extracted to create a file suitable for import into
    https://www.racingrulesofsailing.org (RRS) as a competitor list.

    As the Sailwave data does not have all data as separate fields a
    post processing of the extracted data using
    https://pypi.org/project/excel-list-transform/ will be required.
    First name and last name shall be separate fields for RRS but
    are combined in the helm name field in the SW export.
    Some rewriting of phone numbers to international format may also
    be needed before RRS import depending on how they entered into SW.

    Here we choose {path} to be the path of to the main line.
    The dictionary key directly following "competitors" could be included
    in the output as a key value, but we choose to exclude it by setting
    "include_key" to false.
    We give the name "Class" to the relative path ["compclass"] in the
    main line record. In a similar way we name columns for the other
    interesting attributes.

    If the path for any column does not exist in the input data, we will flag
    it as an error (instead of giving that column an empty value). This
    is done with the "missing_input_for_column" configuration parameter.

    In this case there will be no linked lines.
    '''
    print(msg, file=file)
    generate_syntax_txt(file=file)
    return 0
