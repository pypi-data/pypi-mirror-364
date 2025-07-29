#! /usr/local/bin/python3
"""Functions for actual extractions of list of columns from JSON or XML."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from typing import Optional, Tuple, Generator, cast, Sequence
import sys
from copy import deepcopy
from datetime import datetime
from functools import cmp_to_key
from excel_list_transform.commontypes import JsonType
from extract_list.extract_config import ExtractConfig, LinkedLineSpec
from extract_list.config_enums import MissingInputForColumn
from extract_list.commontypes import Data, Row, Value


class MainDataLine:  # pylint: disable=too-few-public-methods
    """Data of main line."""

    def __init__(self, complete_line: JsonType, key: str | int, row: Row):
        """Construct MainData with data of main line."""
        self.complete_line: JsonType = complete_line
        self.key: str | int = key
        self.row: Row = row


class PathNotInData(KeyError):
    """Exception for path not in in indata."""


def get_at_path(indata: JsonType, path: list[str],
                missing: MissingInputForColumn) -> Optional[JsonType]:
    """Get the data at path in JSON indata."""
    assert len(path) >= 1
    pkey = path[0]
    if not isinstance(indata, dict):
        print('Input data does not match configuration.',
              file=sys.stderr)
        print(f'Trying to extract data at {path} in data that is ' +
              f'{type(indata).__name__} and not dict.',
              file=sys.stderr)
        print(f'indata={indata}', file=sys.stderr)
        sys.exit(1)
    assert isinstance(indata, dict)
    if pkey not in indata:
        if missing == MissingInputForColumn.ERROR:
            print(f'No such key "{pkey}" in relevant section in input data.',
                  file=sys.stderr)
            sys.exit(1)
        else:
            return None
    if len(path) > 1:
        return get_at_path(indata[pkey], path[1:], missing=missing)
    return indata[pkey]


def set_at_path(data: JsonType, path: Sequence[str | int],
                newdata: JsonType) -> None:
    """Set newdata at path in data, modifying data."""
    assert isinstance(path, list)
    assert isinstance(data, (list, dict))
    assert len(path) > 0
    if len(path) > 1:
        set_at_path(data=data[path[0]], path=path[1:], newdata=newdata)
    else:
        data[path[0]] = newdata


def expand_line(skey: Value, dline: JsonType,
                expand: list[list[str]]) -> Generator[Tuple[Value, JsonType],
                                                      None, None]:
    """Expand json line to several lines."""
    assert isinstance(expand, list)
    if not expand:
        yield (skey, dline)
        return
    local_expand = deepcopy(expand)
    local_dline = deepcopy(dline)
    path = local_expand[0]
    assert isinstance(path, list)
    atpath = get_at_path(indata=local_dline, path=path,
                         missing=MissingInputForColumn.EMPTY)
    if atpath is None:
        for ekey, eline in expand_line(skey=skey, dline=local_dline,
                                       expand=expand[1:]):
            yield (ekey, eline)
        return
    alt = deepcopy(atpath)
    if isinstance(alt, list):
        for elem in alt:
            set_at_path(local_dline, path, elem)
            for ekey, eline in expand_line(skey=skey, dline=local_dline,
                                           expand=expand[1:]):
                yield (ekey, eline)
        return
    yield (skey, local_dline)


def get_lines(indata: JsonType, missing: MissingInputForColumn,
              path: list[str],
              expand_at: list[list[str]]) -> Generator[Tuple[Value, JsonType],
                                                       None, None]:
    """Get (as generator) all items in indata under path."""
    lines: JsonType = get_at_path(indata=indata, path=path, missing=missing)
    if lines is None:
        yield (0, None)
        return
    assert lines is not None
    if not isinstance(lines, (list, dict)):
        yield (0, lines)  # single value at path
        return
    assert isinstance(lines, (list, dict))
    if isinstance(lines, list):
        assert isinstance(lines, list)
        llines: list[JsonType] = lines
        for key, dat in enumerate(llines):
            yield (key, dat)
    elif isinstance(lines, dict):
        assert isinstance(lines, dict)
        dlines: dict[str | int, JsonType] = \
            cast(dict[str | int, JsonType], lines)
        for skey, ddat in dlines.items():
            if not isinstance(skey, (int, str)):
                print(f'Key "{skey}" is not str or int as expected',
                      file=sys.stderr)
                sys.exit(1)
            assert isinstance(skey, (int, str))
            ddat = dlines[skey]
            if len(expand_at) == 0:
                yield (skey, ddat)
            else:
                for expkey, expline in expand_line(skey, ddat, expand_at):
                    yield (expkey, expline)
    else:  # pragma: no cover
        print('internal error in get_line()', file=sys.stderr)
        print(f'lines is {type(lines).__name__}', file=sys.stderr)
        sys.exit(1)


def get_columns(inline: JsonType, colspec: dict[str, list[str]],
                missing: MissingInputForColumn) -> Row:
    """Map data in input line to columns."""
    ret: Row = {}
    for colname, path in colspec.items():
        assert isinstance(path, list)
        val = get_at_path(indata=inline, path=path, missing=missing)
        if isinstance(val, (list, dict)):
            print(f'Expected a single value for {colname} at {path}\n',
                  f'but found data of type {type(val).__name__}',
                  file=sys.stderr)
            sys.exit(1)
        assert not isinstance(val, (list, dict))
        ret[colname] = val
    return ret


def extract_main_line(indata: JsonType,
                      cfg: ExtractConfig) -> Generator[MainDataLine,
                                                       None, None]:
    """Extract columns with values according to main_line spec."""
    for key, line in get_lines(indata=indata,
                               missing=cfg.missing_input_for_column,
                               path=cfg.main_line.line,
                               expand_at=cfg.main_line.expand_at):
        if line is None:
            print('No data matching main line in input', file=sys.stderr)
            print(f'Main line path is {cfg.main_line.line}',
                  file=sys.stderr)
            sys.exit(1)
        assert line is not None
        if not isinstance(key, (int, str)):  # pragma no cover
            print(f'Key "{key}" is not str or int as expected',
                  file=sys.stderr)
            sys.exit(1)
        assert isinstance(key, (int, str))
        row = get_columns(inline=line, colspec=cfg.main_line.columns,
                          missing=cfg.missing_input_for_column)
        if cfg.include_key:
            row[cfg.column_name_for_key] = key
        yield MainDataLine(complete_line=line, key=key,
                           row=row)


def create_none_columns(colspec: dict[str, list[str]]) -> Row:
    """Create a row with columns and None values."""
    ret: Row = {key: None for key in colspec.keys()}
    return ret


def extract_linked_line(indata: JsonType, main_line: MainDataLine,
                        cfg: ExtractConfig,
                        linked_spec: LinkedLineSpec) -> Data:
    """Extract columns (with values) for linked lines from input data."""
    if not linked_spec.columns:
        return [{}]
    ret: Data = []
    main_match_value = get_at_path(indata=main_line.complete_line,
                                   path=linked_spec.linked_main_column,
                                   missing=MissingInputForColumn.ERROR)
    for _, line in get_lines(indata=indata,
                             missing=cfg.missing_input_for_column,
                             path=linked_spec.line,
                             expand_at=linked_spec.expand_at):
        if line is None:
            break
        assert line is not None
        link_match_val = get_at_path(indata=line,
                                     path=linked_spec.linked_column,
                                     missing=MissingInputForColumn.ERROR)
        if link_match_val == main_match_value:
            row = get_columns(inline=line, colspec=linked_spec.columns,
                              missing=cfg.missing_input_for_column)
            ret.append(row)
    if not ret:
        if cfg.missing_input_for_column == MissingInputForColumn.ERROR:
            print('Input data not consistent with configuration.',
                  file=sys.stderr)
            print(f'No linked line has {linked_spec.linked_column} ' +
                  f' with value {main_match_value}', file=sys.stderr)
            sys.exit(1)
        else:
            ret.append(create_none_columns(colspec=linked_spec.columns))
    return ret


def add_from_linked_to_main(from_main: Data, from_linked: Data) -> Data:
    """Add lines from linked to lines from main."""
    assert len(from_linked) > 0
    assert len(from_main) > 0
    if len(from_linked) == 1:
        for row in from_main:
            row.update(from_linked[0])
        return from_main
    ret: Data = []
    for linkline in from_linked:
        mainline = deepcopy(from_main)
        for row in mainline:
            row.update(deepcopy(linkline))
        ret.extend(mainline)
    return ret


class RowCompare:  # pylint: disable=too-few-public-methods
    """Function object class to compare rows for sorting."""

    def __init__(self, cols: list[str]) -> None:
        """Construct object that will be used to compare rows."""
        self.cols: list[str] = cols

    def compare(self,  # pylint: disable=too-many-return-statements
                left_row: Row, right_row: Row) -> int:
        """Compare two Rows."""
        for col in self.cols:
            left = left_row[col]
            right = right_row[col]
            if left is None and right is not None:
                return -1
            if left is not None and right is None:
                return 1
            if left is None and right is None:
                continue
            assert left is not None  # keep mypy happy
            assert right is not None  # keep mypy happy
            if isinstance(left, (str, datetime)) or \
               isinstance(right, (str, datetime)):
                # keep mypy happy
                if str(left) < str(right):
                    return -1
                if str(right) < str(left):
                    return 1
            else:
                assert not isinstance(left, (str, datetime))
                assert not isinstance(right, (str, datetime))
                if left < right:
                    return -1
                if right < left:
                    return 1
        return 0


def sort_rows(data: Data, cfg: ExtractConfig) -> Data:
    """Sort the rows in data as configured."""
    cmp = RowCompare(cfg.get_order_rows_by())
    return sorted(data, key=cmp_to_key(cmp.compare))


def extract_data(indata: JsonType, cfg: ExtractConfig) -> Data:
    """Extract columns (with values) from input data."""
    data: Data = []
    for row in extract_main_line(indata=indata, cfg=cfg):
        data_for_row: Data = [row.row]
        for linked_spec in cfg.linked_lines:
            linkdata = extract_linked_line(indata=indata, main_line=row,
                                           cfg=cfg, linked_spec=linked_spec)
            assert len(linkdata) > 0
            if len(linkdata) > 1:
                if cfg.one_output_line_per_main_line:
                    print('Several linked lines match one main line, ' +
                          'but configuration says one line per main line',
                          file=sys.stderr)
                    sys.exit(1)
            data_for_row = add_from_linked_to_main(from_main=data_for_row,
                                                   from_linked=linkdata)
        data.extend(data_for_row)
    return sort_rows(data=data, cfg=cfg)
