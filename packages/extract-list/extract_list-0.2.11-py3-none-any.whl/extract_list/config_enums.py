#! /usr/local/bin/python3
"""Enumerations used in configuration."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from enum import Enum, auto
from excel_list_transform.config_enums import FileType as ExcFileType


class InFileType(Enum):
    """Input file type."""  # Code duplication due to mypy limitation

    JSON = len(ExcFileType) + 1
    XML = auto()


class OutFileType(Enum):
    """Output file type."""  # Code duplication due to mypy limitation

    EXCEL = ExcFileType.EXCEL.value
    CSV = ExcFileType.CSV.value
    JSON = InFileType.JSON.value
    XML = InFileType.XML.value
    TXT = auto()


class MissingInputForColumn(Enum):
    """What to do if path for column does not exist."""

    ERROR = auto()
    EMPTY = auto()
