#! /usr/local/bin/python3
"""Generate text describing example configuration."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from typing import TextIO
from extract_list.config_enums import OutFileType
from extract_list.commontypes import CfgTypes
from extract_list.generate_txt_syntax import generate_syntax_txt
from extract_list.generate_txt_ex_common import \
    EX1_ORDERS, EX1_CUST_AND_REST, EX2_CUST, EX2_ORDERS_AND_REST, \
    DELIVERY_COL, EXAMPLE1_INTRO, EXAMPLE2_INTRO


EXAMPLE_JSON = '''

This example is based on JSON input data in this format:

{
  "customers": [
    {
      "name": "Donald Duck",
      "address": { "street": "Some Road", "number": 666 },
      "customer_number": 66
    },
    {
      "name": "Mickey Mouse",
      "address": { "street": "Another Street", "number": 7 },
      "customer_number": 22
    }
  ],
  "orders": {
    "123": {
      "items": [ { "item": "apple", "quantity": 5 } ],
      "customer": 66
    },
    "234": {
      "items": [
        { "item": "banana", "quantity": 1 },
        { "item": "orange", "quantity": 6 }
      ],
      "customer": 22
    },
    "345": {
      "items": [
        { "item": "carrot", "quantity": 2 },
        { "item": "orange", "quantity": 20 }
      ],
      "customer": 66
    }
  },
  "delivery_method": [
    { "for_street": "Another Street", "deliver_by": "bike" },
    { "for_street": "Some Road", "deliver_by": "car" }
  ]
}

'''

ORDERS_MAIN_LINE_JSON = '''

Here we choose "orders" to be the path of to the main line.
In the following description we refer to this main line record
as the order record.'''

CUST_MAIN_LINE_JSON = '''

Here we choose "customers" to be the path to main line.
In the following description we refer to this main line record
as the customer record.'''

CUST_LLINE_JSON = '''

We choose "customers" as the single linked line in "linked_lines".
In the following description we refer to this linked line record
as the customer record.'''

ORDERS_LLINE_JSON = '''

We choose "orders" as one linked line in "linked_lines".
In the following description we refer to this linked line record
as the order record'''


def generate_txt_example_json(file: TextIO, cfgtype: CfgTypes,
                              outtype: OutFileType) -> int:
    """Write text describing configuration example_json."""
    assert cfgtype == CfgTypes.EXAMPLE_JSON
    msg = EXAMPLE1_INTRO + \
        f'The example will create an output file in {outtype.name} format.'
    msg += EXAMPLE_JSON + ORDERS_MAIN_LINE_JSON + EX1_ORDERS
    msg += CUST_LLINE_JSON + EX1_CUST_AND_REST
    print(msg, file=file)
    generate_syntax_txt(file=file)
    return 0


def generate_txt_example2_json(file: TextIO, cfgtype: CfgTypes,
                               outtype: OutFileType) -> int:
    """Write text describing configuration example_json."""
    assert cfgtype == CfgTypes.EXAMPLE2_JSON
    msg = EXAMPLE2_INTRO + \
        f'The example will create an output file in {outtype.name} format.'
    msg += EXAMPLE_JSON + CUST_MAIN_LINE_JSON + EX2_CUST
    msg += ORDERS_LLINE_JSON + EX2_ORDERS_AND_REST
    msg += '\nWe choose "delivery_method" as the second linked line.'
    msg += DELIVERY_COL
    print(msg, file=file)
    generate_syntax_txt(file=file)
    return 0
