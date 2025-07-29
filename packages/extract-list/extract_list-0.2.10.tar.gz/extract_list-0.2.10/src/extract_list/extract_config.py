#! /usr/local/bin/python3
"""Configuration of extract a list of columns from JSON or XML."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from typing import Optional, TypeAlias, TypeVar, TypedDict, cast
from enum import Enum
from csv import Dialect
import sys
from string import whitespace
from copy import deepcopy
from collections import Counter
from excel_list_transform.config import Config, ParseConverter
from excel_list_transform.config_enums import ExcelLib
from excel_list_transform.str_to_enum import string_to_enum_best_match
from extract_list.config_enums import InFileType, OutFileType, \
    MissingInputForColumn

CsvSpec: TypeAlias = dict[str, Optional[str]]


MLineDict = TypedDict('MLineDict', {'line': list[str],
                                    'columns': dict[str, list[str]],
                                    'expand_at': list[list[str]]})
LLineDict = TypedDict('LLineDict', {'line': list[str],
                                    'columns': dict[str, list[str]],
                                    'linked_main_column': list[str],
                                    'linked_column': list[str],
                                    'expand_at': list[list[str]]})


class MainLineSpec:  # pylint: disable=too-few-public-methods
    """Some spec."""

    def __init__(self, data: Optional[MLineDict] = None):
        """Construct mainline spec."""
        self.line: list[str] = []
        self.columns: dict[str, list[str]] = {}
        self.expand_at: list[list[str]] = []
        if data is not None:
            self.line = data['line']
            self.columns = data['columns']
            self.expand_at = data['expand_at']

    def __str__(self) -> str:
        """Get string representation."""
        return 'MainLineSpec(' + str(self.__dict__) + ')'


class LinkedLineSpec:  # pylint: disable=too-few-public-methods
    """other spec."""

    def __init__(self, data: Optional[LLineDict] = None):
        """Construct linked line spec."""
        self.line: list[str] = []
        self.columns: dict[str, list[str]] = {}
        self.linked_main_column: list[str] = []
        self.linked_column: list[str] = []
        self.expand_at: list[list[str]] = []
        if data is not None:
            self.line = data['line']
            self.columns = data['columns']
            self.linked_main_column = data['linked_main_column']
            self.linked_column = data['linked_column']
            self.expand_at = data['expand_at']

    def __str__(self) -> str:
        """Get string representation."""
        return 'LinkedLineSpec(' + str(self.__dict__) + ')'


class LinkedLineList(list[LinkedLineSpec]):
    """Type trick for JSON parser."""


SomeNamedTuple = TypeVar('SomeNamedTuple', MainLineSpec, LinkedLineSpec)
SomeCfgTyp = TypeVar('SomeCfgTyp')


def _mline_spec_from_dict(data: MLineDict) -> MainLineSpec:
    """Get named tuple converted from dict."""
    return MainLineSpec(data=data)


def _linked_line_from_json_array(data: list[LLineDict]) -> LinkedLineList:
    """Get list of LinkedLineSpec from list of dict."""
    assert isinstance(data, list)
    ret = []
    for elem in data:
        ret.append(LinkedLineSpec(data=elem))
    return LinkedLineList(ret)


class ExtractConfig(Config):  # pylint: disable=too-many-instance-attributes
    """Configuration of extract a list of columns from JSON or XML."""

    @staticmethod
    def example_main_line() -> MainLineSpec:
        """Get example spec for main line."""
        main_col = {'What': ['items', 'item'],
                    'How many': ['items', 'quantity']}
        data: MLineDict = {'line': ['orders'], 'columns': main_col,
                           'expand_at': [['items']]}
        return MainLineSpec(data=data)

    @staticmethod
    def example_linked_line() -> LinkedLineSpec:
        """Get example spec for linked line."""
        columns = {'Customer name': ['name'],
                   'Street': ['address', 'street'],
                   'Street number': ['address', 'number']}
        data: LLineDict = {'line': ['customers'], 'columns': columns,
                           'linked_main_column': ['customer'],
                           'linked_column': ['customer_number'],
                           'expand_at': []}
        return LinkedLineSpec(data=data)

    def __init__(self,  from_json_data_text: Optional[str] = None,
                 from_json_filename: Optional[str] = None) -> None:
        """Construct extract configuration object."""
        self.infile_type: InFileType = InFileType.JSON
        self.infile_encoding: str = 'utf-8'
        self.in_xml_strip_at: bool = False
        self.include_key: bool = True
        self.column_name_for_key: str = 'key col'
        self.missing_input_for_column: MissingInputForColumn = \
            MissingInputForColumn.EMPTY
        self.main_line: MainLineSpec = self.example_main_line()
        self.linked_lines: list[LinkedLineSpec] = [self.example_linked_line()]
        self.one_output_line_per_main_line: bool = True
        self.outfile_type: OutFileType = OutFileType.EXCEL
        self.outfile_encoding: str = 'utf-8'
        self.outfile_excel_library: ExcelLib = ExcelLib.PYLIGHTXL
        self.column_order: list[str] = ['What', 'How many', 'Customer name',
                                        'Street', 'Street number', 'key col']
        self.order_rows_by: list[str] = []
        self.out_xml_attributes = ['What']
        self.out_csv_dialect: CsvSpec = {'name': 'csv.excel',
                                         'delimiter': ',', 'quoting': None,
                                         'quotechar': '"',
                                         'lineterminator': None,
                                         'escapechar': None}
        super().__init__(from_json_data_text=from_json_data_text,
                         from_json_filename=from_json_filename)
        self._check_self()

    def get_out_csv_dialect(self) -> type[Dialect]:
        """Get CSV dialect for outpyt file."""
        assert self.out_csv_dialect['name'] is not None
        return self.get_csv_dialect(**self.out_csv_dialect)

    def _check_self(self) -> None:
        """Check that configuration is OK after reading from file or str."""
        self._check_filetype(self.infile_type, InFileType)
        self.check_char_encoding(self.infile_encoding)
        self._check_filetype(self.outfile_type, OutFileType)
        self.check_char_encoding(self.outfile_encoding)
        self._check_type(self.in_xml_strip_at, bool, 'in_xml_strip_at')
        self._check_type(self.include_key, bool, 'include_key')
        self._check_type(self.column_name_for_key, str, 'column_name_for_key')
        self._check_enum(self.missing_input_for_column, MissingInputForColumn,
                         'missing_input_for_column')
        self._check_type(self.main_line, MainLineSpec, 'main_line')
        self._check_mainline_part(var=self.main_line, spectype=MainLineSpec,
                                  varname='main_line')
        self._check_type(self.linked_lines, list, 'linked_lines')
        self._check_linkedline(self.linked_lines, 'linked_lines')
        self._check_type(self.one_output_line_per_main_line, bool,
                         'one_output_line_per_main_line')
        self._check_enum(self.outfile_excel_library, ExcelLib,
                         'outfile_excel_library')
        self._check_type(self.column_order, list, 'column_order')
        self._check_list_str(self.column_order, 'column_order')
        self._check_type(self.order_rows_by, list, 'order_rows_by')
        self._check_list_str(self.order_rows_by, 'order_rows_by')
        self.check_no_duplicates(self.column_order, 'column_order')
        self._check_type(self.out_xml_attributes, list, 'out_xml_attributes')
        self._check_list_str(self.out_xml_attributes, 'out_xml_attributes')
        self.check_csv()
        self.check_extract_unique_colnames()
        self.cross_check_columns()
        self.cross_check_attrs()
        self.check_valid_xml_colnames()

    def _extracted_columns(self) -> list[str]:
        """Get list names of all extracted columns."""
        extracted_cols: list[str] = []
        for link in self.linked_lines:
            extracted_cols += link.columns.keys()
        extracted_cols += self.main_line.columns.keys()
        if self.include_key:
            extracted_cols.append(self.column_name_for_key)
        return extracted_cols

    def get_order_rows_by(self) -> list[str]:
        """Get list of columns to use for sorting rows."""
        if self.order_rows_by:
            return self.order_rows_by
        return self.column_order

    def cross_check_attrs(self) -> None:
        """Check that out_xml_attributes refer to existing 'columns'."""
        extracted_cols = self._extracted_columns()
        for att in self.out_xml_attributes:
            if att not in extracted_cols:
                print(f'Attribute name "{att}" in out_xml_attributes\n' +
                      'but no column with that name extracted',
                      file=sys.stderr)
                sys.exit(1)

    def cross_check_columns(self) -> None:
        """Do cross-check column order to extracted columns."""
        extracted_cols = self._extracted_columns()
        for col in self.column_order:
            if col not in extracted_cols:
                print(f'column order includes column "{col}"\n' +
                      'but that column is not extracted', file=sys.stderr)
                sys.exit(1)
        for col in extracted_cols:
            if col not in self.column_order:
                print(f'Extracted column "{col}" is missing in column_order',
                      file=sys.stderr)
                sys.exit(1)
        for col in self.order_rows_by:
            if col not in extracted_cols:
                print(f'order rows by includes column "{col}"\n' +
                      'but that column is not extracted', file=sys.stderr)
                sys.exit(1)

    def check_extract_unique_colnames(self) -> None:
        """Check that not several extracted columns have same name."""
        col_names = self._extracted_columns()
        repeated = [k for k, v in Counter(col_names).items() if v > 1]
        if repeated:
            print('Column names of extracted data must be unique.',
                  file=sys.stderr)
            print('Repeated column name(s): ' + ' ,'.join(repeated),
                  file=sys.stderr)
            sys.exit(1)

    def check_valid_xml_colnames(self) -> None:
        """Check and warn for column names that are not valid XML."""
        if self.outfile_type != OutFileType.XML:
            return
        for colname in self.column_order:
            if True in [c in colname for c in whitespace]:
                msg = f'Warning: Column name "{colname}" is not a valid ' +\
                    f'column name in XML,\nas "{colname}" contains white' +\
                    ' space.'
                print(msg, file=sys.stderr)

    def check_csv(self) -> None:
        """Check if CSV configuration is OK."""
        try:
            _ = self.get_out_csv_dialect()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print('Configured out_csv_dialect is not valid', file=sys.stderr)
            print(str(exc), file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def _check_mainline_part(var: MainLineSpec | LinkedLineSpec,
                             spectype:
                             type[MainLineSpec] | type[LinkedLineSpec],
                             varname: str) -> None:
        """Check MainLineSpec or MainLineSpec part of LinkedLineSpec."""
        if not isinstance(var, spectype):
            print(f'Expected {spectype.__name__} for {varname}, but found: \n'
                  f'{var}\nof type {type(var).__name__}',
                  file=sys.stderr)
            sys.exit(1)
        ExtractConfig._check_list_str(var.line, 'line in ' + varname)
        ExtractConfig._check_dict_str_lst_str(var.columns,
                                              'columns in ' + varname)

    @staticmethod
    def _check_linkedline(var: LinkedLineList | list[LinkedLineSpec],
                          varname: str) -> None:
        """Check that we have correct LinkedLineSpec list."""
        if not isinstance(var, list):
            print(f'Expected a list of LinkedLineSpec in {varname}\n' +
                  f'but found: {var}\nof type {type(var).__name__}',
                  file=sys.stderr)
            sys.exit(1)
        for elem in var:
            vname = 'element in ' + varname
            ExtractConfig._check_mainline_part(var=elem,
                                               spectype=LinkedLineSpec,
                                               varname=vname)
            ExtractConfig._check_list_str(elem.linked_main_column,
                                          'linked_main_column in ' + vname)
            ExtractConfig._check_list_str(elem.linked_column,
                                          'linked_column in ' + vname)

    @staticmethod
    def _check_dict_str_lst_str(var: dict[str, list[str]],
                                varname: str) -> None:
        """Check that var is dict[str, list[str]]."""
        if not isinstance(var, dict):
            print(f'Expected a dict of strings to lists in {varname}\n' +
                  f'but found: {var}\nof type {type(var).__name__}',
                  file=sys.stderr)
            sys.exit(1)
        for key, value in var.items():
            if not isinstance(key, str):
                print(f'Expected a dict of strings to lists in {varname}\n' +
                      f'but found key: {key}\nof type {type(key).__name__}',
                      file=sys.stderr)
                sys.exit(1)
            ExtractConfig._check_list_str(value, key + ' in ' + varname)

    @staticmethod
    def _check_list_str(var: list[str], varname: str) -> None:
        """Check that variable is list of str."""
        if not isinstance(var, list):
            print(f'Expected a list of strings in {varname}\n' +
                  f'but found: {var}\nof type {type(var).__name__}',
                  file=sys.stderr)
            sys.exit(1)
        for elem in var:
            if not isinstance(elem, str):
                print(f'Expected a list of strings in {varname}\n' +
                      f'but found element: {elem}\n' +
                      f'of type {type(elem).__name__}',
                      file=sys.stderr)
                sys.exit(1)

    @staticmethod
    def _check_enum(var: Enum, enum_type: type[Enum], varname: str) -> None:
        """Check that config variable is correct enum type."""
        ExtractConfig._check_type(var=var, oftype=enum_type, varname=varname)
        if var not in enum_type:  # pragma: no cover
            allowed = ' ,'.join(list(enum_type))
            print(f'{varname} value {var} is not one of allowed: {allowed}',
                  file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def _check_type(var: SomeCfgTyp, oftype: type[SomeCfgTyp],
                    varname: str) -> None:
        """Check that config variable is of type."""
        if not isinstance(var, oftype):
            print(f'Configuration parameter "{varname}" has wrong type. ',
                  file=sys.stderr)
            print(f'Type is "{type(var).__name__}", ' +
                  f'but expected type "{oftype.__name__}".', file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def _check_filetype(ftype: InFileType | OutFileType,
                        enum_type:
                        type[InFileType] | type[OutFileType]) -> None:
        """Check that file types are OK."""
        if not isinstance(ftype, enum_type):
            print(f'File type {ftype} is not of type {enum_type.__name__}',
                  file=sys.stderr)
            sys.exit(1)
        if ftype not in enum_type:  # pragma: no cover
            allowed = ' ,'.join(list(enum_type))
            print(f'File type {ftype} is not one of allowed types: {allowed}',
                  file=sys.stderr)
            sys.exit(1)

    @staticmethod
    def get_converter_dict(enum_type: type[Enum]) -> ParseConverter:
        """Get dict for converting to given enum_type."""
        return ParseConverter(result_type=enum_type,
                              func=string_to_enum_best_match,
                              args={'num_type': enum_type})

    @staticmethod
    def get_converter_mainline(nttype: type[MainLineSpec]) -> ParseConverter:
        """Get dict for converting to given namedtuple type."""
        return ParseConverter(result_type=nttype,
                              func=_mline_spec_from_dict,
                              args={})

    @staticmethod
    def get_converter_linkedline() -> ParseConverter:
        """Get dict for converting to linked_lines."""
        return ParseConverter(result_type=LinkedLineList,
                              func=_linked_line_from_json_array,
                              args={})

    def parse_converters(self) -> dict[str, ParseConverter]:
        """Get converters for use when parsing JSON.

        Overriding in derived class.
        Return None if no conversions.
        Return dict of dict for use in json decoder hook.
        Structure of return value shall be:
        {key: {'result type': res_type, 'func': function,
        'args': {arg_name: arg_value}}}.
        """
        return {'infile_type': self.get_converter_dict(InFileType),
                'outfile_type': self.get_converter_dict(OutFileType),
                'outfile_excel_library': self.get_converter_dict(ExcelLib),
                'missing_input_for_column':
                    self.get_converter_dict(MissingInputForColumn),
                'main_line': self.get_converter_mainline(MainLineSpec),
                'linked_lines': self.get_converter_linkedline()}

    def as_json_string(self) -> str:
        """Get JSON string representing this object."""
        if isinstance(self.main_line, dict):
            return super().as_json_string()
        adjusted = deepcopy(self)
        # intentionally violating typing to get wanted JSON
        adjusted.main_line = cast(MainLineSpec, self.main_line.__dict__)
        adjusted.linked_lines = []
        for i in self.linked_lines:
            # intentionally violating typing to get wanted JSON
            adjusted.linked_lines.append(cast(LinkedLineSpec, i.__dict__))
        return adjusted.as_json_string()
