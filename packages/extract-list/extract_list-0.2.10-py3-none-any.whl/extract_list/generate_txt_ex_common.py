#! /usr/local/bin/python3
"""Text describing example configuration for both JSON and XML."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License


EXAMPLE1_INTRO = '''
This is an example created especially to demonstrate how to use the
configuration file with extract_list.
'''

EXAMPLE2_INTRO = '''
This is another example created especially to demonstrate how to
use the configuration file with extract_list.
'''


ORDERS_KEY_COL = '''
The dictionary key directly following "orders" will be included in the
output with the column name "key col".'''

ORDERS_COLUMNS = '''
We give the name "What" to the relative path ["items", "item"] in the
order record. We give the name "How many" to the relative path
["items", "item"] in the order record.
We notice that as each order may contain several items we need to
do "expand_at" the relative path ["items"] to be able to include
the purchased items in the list of columns we have as output format.
'''

EX1_ORDERS = ORDERS_KEY_COL + ORDERS_COLUMNS

CUSTOMERS_COLUMNS = '''
We give the name "Customer name" to the relative path ["name"] in the
customer record. We give the name "Street" to the relative path
["address", "street"] in the customer record. We give the name
"Street number" to the relative path ["address", "number"] in the
customer record. We do not want any "expand_at" in the customer
record so we specify "expand_at" as an empty list.'''

LINK_MAIN_CUST_TO_ORDER = '''
The relative path ["customer number"] in the main line customer records
is tied to the relative path ["customer"] in the linked line order records,
using "linked_column" with value ["customer"] and
"linked_main_column" with value ["customer number"].

'''

LINK_MAIN_ORDER_TO_CUST = '''
The relative path ["customer number"] in the linked line customer records
is tied to the relative path ["customer"] in the main line order records,
using "linked_column" with value ["customer number"] and
"linked_main_column" with value ["customer"].

'''


NONEXIST_EMPTY = '''
If the path for any column does not exist in the input data, that
column will be given an empty value (instead of seeing it as an
error).

'''

ONE_PER_MAIN = '''
"one_output_line_per_main_line" is set to true, meaning that
it will be an error if several linked lines map to the same
main line.
'''

MANY_PER_MAIN = '''
"one_output_line_per_main_line" is set to false, meaning that
it will be OK to have several linked lines map to the same
main line. This is needed as one customer may have several
orders.
'''

DELIVERY_COL = '''
We give the column name "Deliver by to the relative path "deliver_by"
in the delivery method linked line.
The relative path ["address", "street] in the main line customer records
is tied to the relative path ["for_street"] in the linked line delivery
method records, using "linked_column" with value ["for_street"] and
"linked_main_column" with value ["address", "street"].
'''

EX1_CUST_AND_REST = CUSTOMERS_COLUMNS + LINK_MAIN_ORDER_TO_CUST + \
    NONEXIST_EMPTY + ONE_PER_MAIN


EX2_CUST = CUSTOMERS_COLUMNS
EX2_ORDERS_AND_REST = ORDERS_COLUMNS + NONEXIST_EMPTY + MANY_PER_MAIN
