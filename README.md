# calgary-homes-parser
A small Python program to parse `calgaryhomes.ca` listing URLs


Instructions
============
External libaries to install:

    $ pip install validators
    $ pip install pandas

Or if on Windows:

    $ py -m pip install validators
    $ py -m pip install pandas

To execute the program:

    $ py house_parser.py

Note: if your Python version < 3.10, any `match-case` conditionals will need to be rewritten as `if-else` statements.

If you have multiple Python versions installed, you will need to specify a version >= 3.10 when executing:

    $ py -3.11 house_parser.py

When prompted, enter a valid listing URL to parse:

    $ Enter CalgaryHomes URL to parse: https://calgaryhomes.ca/listing/....../

The program will parse the html page for relevant listing details, and ask if you wish to continue providing URLS to parse:

    $ Continue? (y/n): y

If you no longer wish to continue, choose the corresponding format option you want your list of houses output to:

    $ Output format options:
    $ [1] csv
    $ [2] xlsx (excel)
    $ [3] json
    $ [4] cli (command line)
    $ Enter number for output choice: 1

The file will then be output with the date in the title:

    $ Outputting House list to csv...
    $ Output file: house_list_output_2025-02-05.csv
