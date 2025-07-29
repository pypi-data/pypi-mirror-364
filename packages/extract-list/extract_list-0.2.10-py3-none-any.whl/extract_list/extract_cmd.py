#! /usr/local/bin/python3
# PYTHON_ARGCOMPLETE_OK
"""Extract a list of columns from JSON or XML and save to excel, CSV, etc."""

# Copyright (c) 2024 - 2025 Tom Björkholm
# MIT License

from sys import argv as sys_argv
from copy import deepcopy
from typing import Optional, TypeAlias
import argparse
import argcomplete
from extract_list.generate_cfg import generate_example_cfg, \
    get_types_of_cfg, get_out_file_types
from extract_list.extract_func import extract_func
from extract_list.xl_version import XlVersion


def gen_cfg_cmd(args: argparse.Namespace) -> int:
    """Generate example cfg file."""
    outfilename: str = args.output[0]
    cfgtype: str = args.kind[0]
    outfiletype: str = args.typeofoutput[0]
    return generate_example_cfg(filename=outfilename,
                                cfgtype=cfgtype,
                                out_file_type=outfiletype)


def do_extract_cmd(args: argparse.Namespace) -> int:
    """Do extraction of list."""
    outfilename = args.output[0]
    infilename = args.input[0]
    cfgfilename = args.cfg[0]
    return extract_func(in_file_name=infilename,
                        out_file_name=outfilename,
                        cfg_file_name=cfgfilename)


def version_cmd(_: argparse.Namespace) -> int:
    """Print version information."""
    vers = XlVersion()
    vers.print()
    return 0


USAGE_ORDER = '''
The normal way to use this command is:
(1) Using the "cfg-example" sub-command a few example configuration (.cfg)
files with description (.txt) files are generated.
(2) Read the example configuration (.cfg) files and the accompanying
description (.txt) files.
(3) Find an example that is close to what you want to achieve.
(4) Modify that configuration file to achieve what you want to achieve.
(5) Use the "extract" sub-command to extract data from input (JSON or XML)
and output it as a list according to your modified configuration
file.
(6) Read the produced output. If necessary go back to step 4 and adjust
how the data is transformed.
'''

TXT_DESCRIPTION = '''
When generating an example configuration file a text file describing
the configuration file syntax is also generated, with the same name
as the configuration file but with extension .txt instead of .cfg.
'''

GENERAL_DESCRIPTION = '''
Extract data from an input file in JSON or XML format, and output
it as a list of columns in Excel, CSV, text, JSON or XML format.
How data is extracted is described in a configuration file.
Name of input file, output file and configuration file is given
as command line arguments.
The command can also generate a few example configuration files.
When generating an example configuration file the output file name
switch gives the name of the generated configuration file.
'''

SEE_MAIN_HELP = '''
See also help text for main command without sub-commands.
'''

SubParseAct: TypeAlias = 'argparse._SubParsersAction[argparse.ArgumentParser]'


def gen_cfg_args(subparsers: SubParseAct) -> None:
    """Add arguments for generate example config sub-command."""
    cfg_help = 'Generate example configuration file (example .cfg file). '
    cfg_help += 'Arguments select the kind of configuration file that '
    cfg_help += 'is generated.'
    cfg_parser = subparsers.add_parser('cfg-example', help=cfg_help,
                                       epilog=USAGE_ORDER,
                                       description=cfg_help +
                                       TXT_DESCRIPTION + SEE_MAIN_HELP)
    cfg_parser.set_defaults(func=gen_cfg_cmd)
    examplekinds = get_types_of_cfg()
    kind_help = 'Kind of example to generate configuration file for.'
    kind_help += 'Possible kinds are (' + ', '.join(examplekinds) + ').'
    cfg_parser.add_argument('-k', '--kind', nargs=1, required=True,
                            help=kind_help, choices=examplekinds)
    outtypes = get_out_file_types()
    out_help = 'What output file format should configuration file '
    out_help += 'specify. '
    out_help += 'Possible values are (' + ', '.join(outtypes) + '). '
    cfg_parser.add_argument('-t', '--typeofoutput', nargs=1, required=True,
                            help=out_help, choices=outtypes)
    cfg_output_help = 'Name of configuration (output) file to create.'
    cfg_parser.add_argument('-o', '--output', nargs=1,
                            help=cfg_output_help, required=True)


def extract_args(subparsers: SubParseAct) -> None:
    """Add arguments for extract sub-command."""
    extract_help = 'Extract list of columns of data from JSON or XML input. '
    extract_help += 'How data is extracted '
    extract_help += 'is described in a configuration file. Name of input '
    extract_help += 'file, output file and configuration file is given as '
    extract_help += 'command line arguments.'
    extract_parser = subparsers.add_parser('extract', help=extract_help,
                                           epilog=USAGE_ORDER,
                                           description=extract_help +
                                           SEE_MAIN_HELP)
    extract_parser.set_defaults(func=do_extract_cmd)
    extract_parser.add_argument('-c', '--cfg', nargs=1, required=True,
                                help='Configuation file name to use.')
    extract_parser.add_argument('-i', '--input', nargs=1,
                                help='Name of input file.', required=True)
    extract_parser.add_argument('-o', '--output', nargs=1,
                                help='Name of output file to create.',
                                required=True)


def version_args(subparsers: SubParseAct) -> None:
    """Add arguments for version sub-command."""
    version_help = 'Only print versions of extract_list '
    version_help += 'and of main modules used by it and of Python.'
    version_parser = subparsers.add_parser('version', help=version_help,
                                           epilog=USAGE_ORDER,
                                           description=version_help +
                                           SEE_MAIN_HELP)
    version_parser.set_defaults(func=version_cmd)


def extract_cmd(arguments: Optional[list[str]] = None) -> int:
    """Extract a list of columns from JSON or XML and save to excel, etc."""
    epimain = 'More detailed help is available for each sub-command.'
    XlVersion().check_if_unsupported_python()
    if arguments is None:  # pragma: no cover
        arguments = sys_argv
    fixed_args = deepcopy(arguments)
    if len(fixed_args) > 2 and 'python' in fixed_args[0]:
        del fixed_args[0]
    if len(fixed_args) > 2 and '-m' == fixed_args[0]:
        del fixed_args[0]
    while len(fixed_args) >= 1 and fixed_args[0][-3:] == '.py':
        del fixed_args[0]
    desc = GENERAL_DESCRIPTION + \
        USAGE_ORDER
    parser = argparse.ArgumentParser(prog='extract_list', description=desc,
                                     epilog=epimain)
    subparsers = parser.add_subparsers(dest='subparser_name', required=True)
    gen_cfg_args(subparsers)
    extract_args(subparsers)
    version_args(subparsers)
    argcomplete.autocomplete(parser)
    args = parser.parse_args(args=fixed_args)
    ret = args.func(args)
    assert isinstance(ret, int)
    return ret
