# Penelope

**Penelope** is a multi-tool for creating, editing and converting dictionaries, especially for eReader devices.

* Version: 2.0.0
* Date: 2014-06-30
* Developer: [Alberto Pettarin](http://www.albertopettarin.it/) ([contact](http://www.albertopettarin.it/contact.html))

With the current version you can:

* convert a dictionary FROM/TO the following formats:
    * Bookeen Cybook Odyssey (R/W)
    * Kobo (R index only, W unencrypted/unobfuscated only)
    * StarDict (R/W)
    * XML (R/W)
    * CSV (R/W)
* merge more dictionaries (of the same type) into a single dictionary
* define your own parser for each word/definition
* define your own collation function when outputting to Bookeen Cybook Odyssey format
* generate an EPUB file containing the index of a given dictionary (e.g., to cope with the lack of a search function on your eReader)

Please note that Penelope needs substantial code refactoring.
Unfortunately, I no longer have time to do that.
Please fork and improve.

Many people have asked for PRC/MOBI support.
Again, I no longer have time to do that.


### Important update (2013-04-27)

Kobo issued a new firmware 2.5.1 (thanks!), which allows you to use unencrypted/unobfuscated dictionaries again, including those produced by Penelope. Some minor bugs in the UI/UX are still present, but at least the custom dictionaries are back!


### Update (2013-04-23)

It seems that Kobo, with firmware 2.5.0, requires the dictionaries to be encrypted/obfuscated. Hence, the dictionaries output by Penelope do not longer work on Kobo devices. I contacted Kobo staff via Twitter, and they forwarded the notice to their development team. I hope they will fix the issue with a new firmware release soon. Meanwhile, if you need your custom-made dictionaries, you must stay with or revert to firmware 2.4.0. 


## Usage

```
$ python penelope.py -p <prefix list> -f <language_from> -t <language_to> [OPTIONS]

Required arguments:
 -p <prefix list>       : list of the dictionaries to be merged/converted (without extension, comma separated)
 -f <language_from>     : ISO 631-2 code language_from of the dictionary to be converted
 -t <language_to>       : ISO 631-2 code language_to of the dictionary to be converted

Optional arguments:
 -d                     : enable debug mode and do not delete temporary files
 -h                     : print this usage message and exit
 -i                     : ignore word case while building the dictionary index
 -z                     : create the .install zip file containing the dictionary and the index
 --sd                   : input dictionary in StarDict format (default)
 --odyssey              : input dictionary in Bookeen Cybook Odyssey format
 --xml                  : input dictionary in XML format
 --kobo                 : input dictionary in Kobo format (reads the index only!)
 --csv                  : input dictionary in CSV format
 --output-odyssey       : output dictionary in Bookeen Cybook Odyssey format (default)
 --output-sd            : output dictionary in StarDict format
 --output-xml           : output dictionary in XML format
 --output-kobo          : output dictionary in Kobo format
 --output-csv           : output dictionary in CSV format
 --output-epub          : output EPUB file containing the index of the input dictionary
 --title <string>       : set the title string shown on the Odyssey screen to <string>
 --license <string>     : set the license string to <string>
 --copyright <string>   : set the copyright string to <string>
 --description <string> : set the description string to <string>
 --year <string>        : set the year string to <string>
 --parser <parser.py>   : use <parser.py> to parse the input dictionary
 --collation <coll.py>  : use <coll.py> as collation function when outputting in Bookeen Cybook Odyssey format
 --fs <string>          : use <string> as CSV field separator, escaping ASCII sequences (default: \t)
 --ls <string>          : use <string> as CSV line separator, escaping ASCII sequences (default: \n)

$ python penelope.py -h
$ python penelope.py           -p foo -f en -t en
$ python penelope.py           -p bar -f en -t it
$ python penelope.py           -p "bar,foo,zam" -f en -t it
$ python penelope.py --xml     -p foo -f en -t en
$ python penelope.py --xml     -p foo -f en -t en --output-sd
$ python penelope.py           -p bar -f en -t it --output-kobo
$ python penelope.py           -p bar -f en -t it --output-xml -i
$ python penelope.py --kobo    -p bar -f it -t it --output-epub
$ python penelope.py --odyssey -p bar -f en -t en --output-epub
$ python penelope.py           -p bar -f en -t it --title "My EN->IT dictionary" --year 2012 --license "CC-BY-NC-SA 3.0"
$ python penelope.py           -p foo -f en -t en --parser foo_parser.py --title "Custom EN dictionary"
$ python penelope.py           -p foo -f en -t en --collation custom_collation.py
$ python penelope.py --xml     -p foo -f en -t en --output-csv --fs "\t\t" --ls "\n" 
```

Please have a look at this web page for details:
http://www.albertopettarin.it/penelope.html

Note: if you want to convert Kobo dictionaries, you need [MARISA](https://code.google.com/p/marisa-trie/).

## License

**Penelope** is released under the MIT License since version 2.0.0 (2014-06-30).

Previous versions, hosted in a [Google Code repo](http://code.google.com/p/penelope-dictionary-converter/),
were released under the GNU GPL 3 License.


## Acknowledgments 

Many thanks to:

* _uwelovesdonna_ for contributing ideas for improving the code and for setting up many pages of the project wiki;
* _Jens Sadowski_ for pointing out a bug with Unicode file names and for suggesting using multiset `dict()` instead of set `dict()`;
* _oldnat_ for pointing out a bug under Windows and Python 3;
* _Wolfgang Miller-Reichling_ for providing the code for reading CSV dictionaries;
* _branok_ for providing the idea and initial code for German collation function;
* _pal_ for suggesting passing `-l` switch to `MARISA_BUILD`;
* _Lukas Brückner_ for suggesting escaping `& < >` when outputting in XML format;
* _Stephan Lichtenhagen_ for suggesting forcing UTF-8 encoding on Python 3.


## Limitations and Missing Features 

* No support for PRC/MOBI dictionaries 
* Input files are assumed to be Unicode UTF-8 encoded
* CWD-dependent 

