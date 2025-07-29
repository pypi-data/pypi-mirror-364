# extract-list

## Background

This python application was born out of the experience that needed data was available as part of JSON or as part of XML files, but the data was needed as a list of columns in excel or CSV (comma separated values) format.

## What it does

This small python application:

* reads data from an XML file or from a JSON file.
* extracts (a configurable part of the) data from the data read
* outputs the extracted data as list with a number of columns in the desired format that can be:
    * Excel
    * CSV (comma separated values)
    * plain text file
    * JSON
    * XML

How this is done is governed by a configuration file. The application can create a number of example configuration files with accompanying description text files.

## Using it

If you want to use it install it using pip from [https://pypi.org/project/extract-list](https://pypi.org/project/extract-list). There is no need download anything from Bitbucket to use the application.

### Installing on mac and Linux

````sh
pip3 install --upgrade extract-list
````

### Installing on Microsoft Windows

````sh
pip install --upgrade extract-list
````

### Information for use

Please see [https://pypi.org/project/extract-list](https://pypi.org/project/extract-list) or please see README_pypi.md

## For developers

### Needed environment

#### OS

For running the script and running the test suite you need a mac or a Linux computer. Even if the resulting application can be installed and used on Windows, the scripts for building and testing is only implemented for mac and Linux.

#### Python version

Please see README_pypi.md for the required python version. Newest Python version is used for master branch.

#### Zsh

The scripts are all zsh. zsh is available by default on modern macs. zsh can easily be installed on Linux (on Ubuntu: sudo apt install zsh).

### Internal APIs not guaranteed

The internal APIs in this package are not guaranteed to be stable. They can change without warning between versions.

### Building application

There are 3 scripts for building the application

* setup_build_environment.zsh
  Run this script first to get the environment set up for building
* doBuild.zsh
  Run this script to build an installation package (.whl) and to run the tests on it in a venv (virtual environment).
* clean.zsh
  Deletes all files that was produced by the build to start over from a clean state.

The "testing" includes pytest, pylint, flake8 and mypy.

After running doBuild.zsh you can open reports/index.htm to see all test reports.

After running doBuild.zsh you can do manual test of the built and installed application in the virtual environment ./venv
