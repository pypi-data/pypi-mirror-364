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

## Installing it

If you want to use it, install it using pip. A precondition is that you have Python installed on you computer. Python can be downloaded from [https://www.python.org/downloads/](https://www.python.org/downloads/).

### Installing on mac and Linux

````sh
pip3 install --upgrade extract-list
````

### Installing on Microsoft Windows

````sh
pip install --upgrade extract-list
````

## Version history

| Version | Date        | Python version  | Description                         |
|---------|-------------|-----------------|-------------------------------------|
| 0.2     | 06 Jan 2025 | 3.12.6 or newer | First released version              |
| 0.2.2   | 23 Mar 2025 | 3.13.2 or newer | Adapted to Python 3.13.2            |
| 0.2.3   | 23 Mar 2025 | 3.13.2 or newer | Fix in README only                  |
| 0.2.5   | 09 Apr 2025 | 3.13.3 or newer | Using newer dependencies            |
| 0.2.7   | 09 Jun 2025 | 3.12.x          | add version sub-command             |
| 0.2.8   | 09 Jun 2025 | 3.13 or newer   | add version sub-command             |
| 0.2.10  | 23 Jul 2025 | 3.12.x          | updated dependencies                |
| 0.2.11  | 23 Jul 2025 | 3.13 or newer   | updated dependencies                |

## Running the application

### Running the application on mac and Linux

````sh
python3 -m extract_list --help
python3 -m extract_list cfg-example --help
python3 -m extract_list extract --help
python3 -m extract_list cfg-example -k sw_json_to_rrs -t excel -o sw-example.cfg
python3 -m extract_list extract -c sw-example.cfg -i input.json -o output.xlsx
````

### Running the application on Microsoft Windows

````sh
python -m extract_list --help
python -m extract_list cfg-example --help
python -m extract_list extract --help
python -m extract_list cfg-example -k sw_json_to_rrs -t excel -o sw-example.cfg
python -m extract_list extract -c sw-example.cfg -i input.json -o output.xlsx
````

## Suggested way to get started

 1. Use the "cfg-example" sub-command to generate a few example configuration (.cfg) files with description (.txt) files.
 2. Read the example configuration (.cfg) files and the accompanying description (.txt) files.
 3. Find an example that is close to what you want to achieve.
 4. Modify that configuration file to achieve what you want to achieve.
 5. Use the "extract" sub-command to read your data and output extracted data according to your modified configuration file.
 6. Read the produced output. If necessary go back to step 4 and adjust how the data is transformed.

### Example configuration files

When using the "cfg-example" sub-command to generate an example configuration file (say example.cfg) a text file describing the configuration and the syntax of the configuration file is also generated. If the example configuration file is named example.cfg, then the text file descriging the configuration is named example.txt.

You can generate several example configuration files each with an accompanying text file descriping it.

Read the text file describing the configuration file while looking at the configuration file to understand the syntax and the possible options.

## Description of how to write/change the configuration file

The configuration file is in JSON syntax [https://en.wikipedia.org/wiki/JSON](https://en.wikipedia.org/wiki/JSON).
The keywords and the nesting is important. The order of keywords have no significance (the examples use alphabetical order). Indentation and line breaks have no significance.

The encoding for the configuration file must be UTF-8. (US-ACII is a subset of UTF-8.)

It is recommended that you let the command generate a configuration file and then edit that file to match your needs. It is NOT recommended that the user writes the configuration file from scratch.

### Type of input file

The type of input file to read is determined by **"infile_type"**. **"infile_type"** can have the values:

* *"JSON"*
* *"XML"*

As both JSON and XML are syntax in text files, the text files can have an encoding for the text in the files
[https://en.wikipedia.org/wiki/Character_encoding](https://en.wikipedia.org/wiki/Character_encoding).
This is specified with **"infile_encoding"**. Unless you know that you need another encoding leave this as in the generated example configuration.

### Type of output file

The type of output file to produce is determined by **"outfile_type"**. **"outfile_type"** can have the values:

* *"EXCEL"*
* *"CSV"*
* *"JSON"*
* *"XML"*
* *"TXT"*

As *CSV, TXT, JSON* and *XML* are syntaxes in text files, the text files can have an encoding for the text in the files
[https://en.wikipedia.org/wiki/Character_encoding](https://en.wikipedia.org/wiki/Character_encoding).
This is specified with **"outfile_encoding"**. Unless you know that you need another encoding leave this as in the generated example configuration.

Comma separated values files (CSV files) may differ slightly depending on the programs used to read/write them and the locale used. **"out_csv_dialect"** changes how CSV files are written. It is always needed in the configuration file, but is only used if the output is CSV.

Excel files can be written using three libraries. **"outfile_excel_library"** can have values *"OPENPYXL"*, *"XLSXWRITER"* or *"PYLIGHTXL"*. These are different third party libraries that can read/write excel. My experience is that "PYLIGHTXL" most often is able to read and write excel files correctly. If you have trouble writing your particular excel file, please try another library. **"outfile_excel_library"** is always needed in the configuration file but is only used if the output is excel.

### Data to extract

The input files (JSON or XML) is likely to include a lot more data than what is interesting to extract. The data to extract is specified using **"main_line"** and **"linked_lines"** parameters in the configuration file.

The **"main_line"** specifies what part of the input file should be the main part of the output line(s). The linked lines have some data linking them to the main line: A linked line is linked to the main line if some item in the linked line has the same value as some other item in the main line.

The **"line"** sub-parameter of the the **"main_line"** and **"linked_lines"** configuration parameters includes a list of strings. This list of strings is the path of keywords to the records. Directly below this path is either a list or a dictionary of the records.

The dictionary of the records of the **"main_line"** are indexed in the input (either by an integer index in the case of a list, or by the key in case of a dictionary). If you want this index (also known as key) to be included in the output, set configuration  parameter **"include_key"** to true. To exclude this index (key) from the output set **"include_key"** to false. The output column name for this key (index) is set using the configuration parameter **"column_name_for_key"**.

The **"columns"** sub-parameter of the **"main_line"** and **"linked_lines"** configuration parameters includes a dictionary from a string to a list of strings. The keys in this dictionary is the column names to use in the output. The list of strings is the relative path in the record of the item that has the value for this column.

Sometimes a single record in the input, defined as the item in the list or dictionary referenced by the **"line"** sub-parameter, can contain several sub-records. For instance if the record is a purchase order, then the order may include several purchased items. As the output format of a list of columns does not support such nesting, the single input redord needs to be split into several output lines. The common items in the input record is then duplicated on all such lines split from the same input record. The configuration sub-parameter **"expand_at"** holds a list of relative paths where the input record should be expanded (or split). Each such relative path is configured using a list of strings in the **"expand_at"** sub-parameter. As the **"expand_at"** holds a list of relative paths (list of list of strings), this expansion can be configured to be done on zero, one or several places in the input record.

There can be only one main line, denoted by the **"main_line"** configuration parameter. In contrast there may be any number of linked lines. The linked lines are described be an array for the the **"linked_lines"** configuration parameter. The sub-parameters described for the **"main_line"** shall also be configured for each item in the **"linked_lines"** array.

How linked lines are tied to main line is defined by the **"linked_column"** and **"linked_main_column"** sub-parameter for each linked line item. Both **"linked_column"** and **"linked_main_column"** are relative paths in the input records using the familiar list of strings syntax. The **"linked_column"** sub-parameter denotes an item in the linked line record that shall have the same value as the item in the main line record denoted by the the **"linked_main_column"** sub-parameter.

The data items used to link a linked line to a main line may be extracted to the output using the **"column"** sub-parameter, but this is totally optional. There is no requirement that the data items used to tie linked lines to main lines are part of the output.

Several linked lines could be tied to the same main line. The configuration parameter **"one_output_line_per_main_line"** determines how this case is handled. If it is set to false, the result will be that the main line part is duplicated so that the output has one line for each tied combination of main line and linked lines. Sometimes this duplication of main line is not intended. By setting the configuration parameter **"one_output_line_per_main_line"** to true, several linked lines tied to one main line will be flagged as an error.

As items in records are optional in the input formats (JSON and XML) it is possible the that there is no data at the paths specified for columns or specified for records. The configuration parameter **"missing_input_for_column"** determines how missing data in input is handled. The possible values are *"EMPTY"* and *"ERROR"*. If configured as *"EMPTY"* the columns resulting from the missing input data will simply be empty.

### XML attributes

The XML syntax allows member values of an object to either be written as nested objects or as attributes. If the input has XML attributes the key for the attributes will have an "@" prepended. To handle this the configuration parameter **"in_xml_strip_at"** can be set to *true* or *false*. If **"in_xml_strip_at"** is set to *true* an "@" character in the beginning of any key will be stripped off.

The configuration parameter **"out_xml_attributes"** specifies a list of column names. These columns will be written as XML attributes in XML output, not as nested objects.

### Output column order

The order of the columns in the output is specified with the configuration parameter **"column_order"**. The value of this parameter is a list of strings.

Specifying a column in the output column order that has not been extracted is an error. It is also an error to extract a column and not specify it in the output column order.

Output line order

The configuration parameter **"order_rows_by"** specifies that lines produced shall be sorted based on these columns. The most significant column shall be first in the list of column names.

The default order or lines produced is to order them based on the list of columns in the **"column_order"** configuration parameter. Leave **"order_rows_by"** as empty list unless you have a reason to request another specific order than the default.

## Source code

Source code and tests are available at [https://bitbucket.org/tom-bjorkholm/extract-list](https://bitbucket.org/tom-bjorkholm/extract-list).
