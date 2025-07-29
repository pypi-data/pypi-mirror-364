#! /usr/local/bin/python3
"""Define types that are common for several files."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from typing import Optional, TypeAlias
from datetime import datetime
from enum import Enum, auto

Value: TypeAlias = Optional[str | int | bool | float | datetime]
Row: TypeAlias = dict[str, Value]
Data: TypeAlias = list[Row]


class CfgTypes(Enum):
    """Types of example configurations."""

    SW_JSON_TO_RRS = auto()
    SW_XML_TO_RRS = auto()
    EXAMPLE_JSON = auto()
    EXAMPLE_XML = auto()
    EXAMPLE2_JSON = auto()
    EXAMPLE2_XML = auto()
