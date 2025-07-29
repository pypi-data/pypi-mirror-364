#! /usr/local/bin/python3
"""Define types that are common for several files."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from excel_list_transform.version_information import VersionInformation


class XlVersion(VersionInformation):
    """Get and print version information."""

    def module_names(self) -> list[str]:
        """Get list of main module names."""
        loc_mods = ['extract_list', 'xmltodict']
        return loc_mods + super().module_names()
