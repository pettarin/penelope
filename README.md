# Penelope

**Penelope** is a multi-tool for creating, editing and converting dictionaries, especially for eReader devices.

* Version: 3.1.1
* Date: 2015-12-02
* Developer: [Alberto Pettarin](http://www.albertopettarin.it/)
* License: the MIT License (MIT)
* Contact: [click here](http://www.albertopettarin.it/contact.html)

With the current version you can:

* convert a dictionary from/to the following formats:
    * Bookeen Cybook Odyssey (R/W)
    * CSV (R/W)
    * EPUB (W only)
    * MOBI (Kindle, W only)
    * Kobo (R index only, W unencrypted/unobfuscated only)
    * StarDict (R/W)
    * XML (R/W)
* merge several dictionaries of the same type into a single dictionary
* merge several definitions for the same headword
* sort by headword and/or by definition
* define your own input parser to merge/sort/edit definitions
* define your own collation function (`bookeen` output format only)
* output an EPUB file containing the dictionary (e.g., to cope with the lack of a search function of your eReader)
* output a MOBI (Kindle) dictionary


### Important updates

* 2015-11-24 Penelope is now available on [PyPI](https://pypi.python.org/pypi/penelope/), bumped version to **3.0.1**
* 2015-11-22 **The command line interface has changed with v3.0.0**, as I performed a huge code refactoring.
* 2014-06-30 I moved Penelope to GitHub, and released it under the MIT License, with the version code v2.0.0.


## Installation

### Using pip

1. Open a console and type:

    ```bash
    $ [sudo] pip install penelope
    ```

2. That's it! Just run without arguments (or with `-h` or `--help`) to get the manual:

    ```bash
    $ penelope
    ```

This procedure will install `lxml` and `marisa-trie`.
You might need to install `dictzip` (StarDict output) and  `kindlegen` (MOBI output) separately, see below.

### From source code

1. Get the source code:

    * clone this repo with `git`:

        ```bash
        $ git clone https://github.com/pettarin/penelope.git
        ```

    * or download the [latest release](https://github.com/pettarin/penelope/releases) and uncompress it somewhere,
    * or download the [current master ZIP](https://github.com/pettarin/penelope/archive/master.zip) and uncompress it somewhere.

2. Open a console and enter the `penelope` (cloned) directory:

    ```bash
    $ cd /path/to/penelope
    ```

3. That's it! Just run without arguments (or with `-h` or `--help`) to get the manual:

    ```bash
    $ python -m penelope
    ```

This procedure will not install any dependencies: you will need to do that manually, see below.


### Dependencies

* Python, version 2.7.x or 3.4.x (or above)

* to write StarDict dictionaries: the `dictzip` executable, available in your `$PATH` or specified with `--dictzip-path`:

    ```bash
    $ [sudo] apt-get install dictzip
    ```

* to read/write Kobo dictionaries: the Python module `marisa-trie`:

    ```bash
    $ [sudo] pip install marisa-trie
    ```

  or [MARISA](https://code.google.com/p/marisa-trie/) executables available in your `$PATH` or specified with `--marisa-bin-path`

* to write MOBI Kindle dictionaries: the [kindlegen](https://www.amazon.com/gp/feature.html?docId=1000765211) executable, available in your `$PATH` or specified with `--kindlegen-path`

* to read/write XML dictionaries: the Python module `lxml`:

    ```bash
    $ [sudo] pip install lxml
    ```


## Usage

```
usage: 
  $ penelope -h
  $ penelope -i INPUT_FILE -j INPUT_FORMAT -f LANGUAGE_FROM -t LANGUAGE_TO -p OUTPUT_FORMAT -o OUTPUT_FILE [OPTIONS]
  $ penelope -i IN1,IN2[,IN3...] -j INPUT_FORMAT -f LANGUAGE_FROM -t LANGUAGE_TO -p OUTPUT_FORMAT -o OUTPUT_FILE [OPTIONS]

description:
  Convert dictionary file(s) with file name prefix INPUT_FILE from format INPUT_FORMAT to format OUTPUT_FORMAT, saving it as OUTPUT_FILE.
  The dictionary is from LANGUAGE_FROM to LANGUAGE_TO, possibly the same.
  You can merge several dictionaries (with the same format), by providing a list of comma-separated prefixes, as shown by the third synopsis above.

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           enable debug mode (default: False)
  -f LANGUAGE_FROM, --language-from LANGUAGE_FROM
                        from language (ISO 639-1 code)
  -i INPUT_FILE, --input-file INPUT_FILE
                        input file name prefix(es). Multiple prefixes must be
                        comma-separated.
  -j INPUT_FORMAT, --input-format INPUT_FORMAT
                        from format (values: bookeen|csv|kobo|stardict|xml)
  -k, --keep            keep temporary files (default: False)
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        output file name
  -p OUTPUT_FORMAT, --output-format OUTPUT_FORMAT
                        to format (values:
                        bookeen|csv|epub|kobo|mobi|stardict|xml)
  -t LANGUAGE_TO, --language-to LANGUAGE_TO
                        to language (ISO 639-1 code)
  -v, --version         print version and exit
  --author AUTHOR       author string
  --copyright COPYRIGHT
                        copyright string
  --cover-path COVER_PATH
                        path of the cover image file
  --description DESCRIPTION
                        description string
  --email EMAIL         email string
  --identifier IDENTIFIER
                        identifier string
  --license LICENSE     license string
  --title TITLE         title string
  --website WEBSITE     website string
  --year YEAR           year string
  --apply-css APPLY_CSS
                        apply the given CSS file (epub and mobi output only)
  --bookeen-collation-function BOOKEEN_COLLATION_FUNCTION
                        use the specified collation function
  --bookeen-install-file
                        create *.install file (default: False)
  --csv-fs CSV_FS       CSV field separator (default: ',')
  --csv-ignore-first-line
                        ignore the first line of the input CSV file(s)
                        (default: False)
  --csv-ls CSV_LS       CSV line separator (default: '\n')
  --dictzip-path DICTZIP_PATH
                        path to dictzip executable
  --epub-no-compress    do not create the compressed container (epub output
                        only, default: False)
  --escape-strings      escape HTML strings (default: False)
  --flatten-synonyms    flatten synonyms, creating a new entry with
                        headword=synonym and using the definition of the
                        original headword (default: False)
  --group-by-prefix-function GROUP_BY_PREFIX_FUNCTION
                        compute the prefix of headwords using the given prefix
                        function file
  --group-by-prefix-length GROUP_BY_PREFIX_LENGTH
                        group headwords by prefix of given length (default: 2)
  --group-by-prefix-merge-across-first
                        merge headword groups even when the first character
                        changes (default: False)
  --group-by-prefix-merge-min-size GROUP_BY_PREFIX_MERGE_MIN_SIZE
                        merge headword groups until the given minimum number
                        of headwords is reached (default: 0, meaning no merge
                        will take place)
  --ignore-case         ignore headword case, all headwords will be lowercased
                        (default: False)
  --ignore-synonyms     ignore synonyms, not reading/writing them if present
                        (default: False)
  --include-index-page  include an index page (epub and mobi output only,
                        default: False)
  --input-file-encoding INPUT_FILE_ENCODING
                        use the specified encoding for reading the raw
                        contents of input file(s) (default: 'utf-8')
  --input-parser INPUT_PARSER
                        use the specified parser function after reading the
                        raw contents of input file(s)
  --kindlegen-path KINDLEGEN_PATH
                        path to kindlegen executable
  --marisa-bin-path MARISA_BIN_PATH
                        path to MARISA bin directory
  --marisa-index-size MARISA_INDEX_SIZE
                        maximum size of the MARISA index (default: 1000000)
  --merge-definitions   merge definitions for the same headword (default:
                        False)
  --merge-separator MERGE_SEPARATOR
                        add this string between merged definitions (default: '
                        | ')
  --mobi-no-kindlegen   do not run kindlegen, keep .opf and .html files
                        (default: False)
  --no-definitions      do not output definitions for EPUB and MOBI formats
                        (default: False)
  --sd-ignore-sametypesequence
                        ignore the value of sametypesequence in StarDict .ifo
                        files (default: False)
  --sd-no-dictzip       do not compress the .dict file in StarDict files
                        (default: False)
  --sort-after          sort after merging/flattening (default: False)
  --sort-before         sort before merging/flattening (default: False)
  --sort-by-definition  sort by definition (default: False)
  --sort-by-headword    sort by headword (default: False)
  --sort-ignore-case    ignore case when sorting (default: False)
  --sort-reverse        reverse the sort order (default: False)

examples:

  $ penelope -i dict.csv -j csv -f en -t it -p stardict -o output.zip
    Convert en->it dictionary dict.csv (in CSV format) into output.zip (in StarDict format)

  $ penelope -i dict.csv -j csv -f en -t it -p stardict -o output.zip --merge-definitions
    As above, but also merge definitions

  $ penelope -i d1,d2,d3 -j csv -f en -t it -p csv -o output.csv --sort-after --sort-by-headword
    Merge CSV dictionaries d1, d2, and d3 into output.csv, sorting by headword

  $ penelope -i d1,d2,d3 -j csv -f en -t it -p csv -o output.csv --sort-after --sort-by-headword --sort-ignore-case
    As above, but ignore case for sorting

  $ penelope -i d1,d2,d3 -j csv -f en -t it -p csv -o output.csv --sort-after --sort-by-headword --sort-reverse
    As above, but reverse the order

  $ penelope -i dict.zip -j stardict -f en -t it -p csv -o output.csv
    Convert en->it dictionary dict.zip (in StarDict format) into output.csv (in CSV format)

  $ penelope -i dict.zip -j stardict -f en -t it -p csv -o output.csv --ignore-synonyms
    As above, but do not read the .syn synonym file if present

  $ penelope -i dict.zip -j stardict -f en -t it -p csv -o output.csv --flatten-synonyms
    As above, but flatten synonyms

  $ penelope -i dict.zip -j stardict -f en -t it -p bookeen -o output
    Convert dict.zip into output.dict.idx and output.dict for Bookeen devices

  $ penelope -i dict.zip -j stardict -f en -t it -p kobo -o dicthtml-en-it
    Convert dict.zip into dicthtml-en-it.zip for Kobo devices

  $ penelope -i dict.csv -j csv -f en -t it -p mobi -o output.mobi --cover-path mycover.png --title "My English->Italian Dictionary"
    Convert dict.csv into a MOBI (Kindle) dictionary, using the specified cover image and title

  $ penelope -i dict.xml -j xml -f en -t it -p mobi -o output.epub
    Convert dict.xml into an EPUB dictionary

  $ penelope -i dict.xml -j xml -f en -t it -p mobi -o output.epub --epub-output-definitions
    As above, but also output definitions
```

You can find ISO 639-1 language codes [here](http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).


## Installing the Dictionaries

### Bookeen Odyssey Devices

For example, suppose you want to use an IT -> EN dictionary.

1. On your PC, produce/download the IT -> EN dictionary files `it-en.dict` and `it-en.dict.idx`.
2. Connect your Odyssey device to your PC via the USB cable.
3. Using your file manager, copy the two files `it-en.dict` and `it-en.dict.idx`
from your PC into the `Dictionaries/` directory on your Odyssey device.
4.  Reboot your Odyssey, open a book in Italian and select a word: the definition in English should appear.
(For this test, select a common word so you are sure it is present in the dictionary!)

Note that the Bookeen dictionary software will select the dictionary
to use by reading the `dc:language` metadata of your eBook.
Make sure your eBooks have the proper `dc:language` metadata,
otherwise the correct dictionary might not be loaded.


### Kobo Devices

At the time of this writing (2015-12-02), Kobo devices will load dictionaries
only if the files have a file name of an official Kobo dictionaries, which are:

* `dicthtml.zip` (EN)
* `dicthtml-de.zip` (DE), `dicthtml-de-en.zip` (DE -> EN), `dicthtml-en-de.zip` (EN -> DE),
* `dicthtml-es.zip` (ES), `dicthtml-es-en.zip` (ES -> EN), `dicthtml-en-es.zip` (EN -> ES),
* `dicthtml-fr.zip` (FR), `dicthtml-fr-en.zip` (FR -> EN), `dicthtml-en-fr.zip` (EN -> FR),
* `dicthtml-it.zip` (IT), `dicthtml-it-en.zip` (IT -> EN), `dicthtml-en-it.zip` (EN -> IT),
* `dicthtml-nl.zip` (NL)
* `dicthtml-ja.zip` (JA), `dicthtml-en-ja.zip` (EN -> JA),
* `dicthtml-pt.zip` (PT), `dicthtml-pt-en.zip` (PT -> EN), `dicthtml-en-pt.zip` (EN -> PT)

(see [this MobileRead thread](http://www.mobileread.com/forums/showthread.php?t=196931))

Hence, if you want to install a custom dictionary produced with Penelope,
you must choose to overwrite one of the official Kobo dictionaries,
effectively loosing the possibility of using the latter.

For example, suppose you want to use a Polish dictionary (`dicthtml-pl.zip`),
while you are not interested in using the official Portuguese one (`dicthtml-pt.zip`).

1. On your PC, produce/download the Polish dictionary `dicthtml-pl.zip`.
2. In your Kobo device, go to the settings and activate the Portuguese dictionary.
3. Connect your Kobo device to your PC via the USB cable.
4. Using your file manager, copy `dicthtml-pl.zip`
from your PC into the `.kobo/dict/` directory on your Kobo device.
(Note that `.kobo` is a hidden directory: you might need to enable
the "show hidden files/directories" setting of your file manager.)
5. Rename `dicthtml-pl.zip` into `dicthtml-pt.zip`.
6. Reboot your Kobo, open a book in Polish and select a word: the definition should appear.
(For this test, select a common word so you are sure it is present in the dictionary!)

Note that if you update the firmware of your Kobo,
the custom dictionaries might be overwritten with the official ones.
Hence, keep a backup copy of your custom dictionaries in a safe place,
e.g. your PC or a SD card.

You can find a list of custom dictionaries, mostly done with Penelope, in
[this MobileRead thread](http://www.mobileread.com/forums/showthread.php?t=232883).


## License

**Penelope** is released under the MIT License since version 2.0.0 (2014-06-30).

Previous versions, hosted by
[Google Code](http://code.google.com/p/penelope-dictionary-converter/),
were released under the GNU GPL 3 License.


## Limitations and Missing Features 

* Bookeen has no official documentation for its dictionary format (it has been reverse-engineered), YMMV
* Kobo has no official documentation for its dictionary format (it has been reverse-engineered), YMMV
* Reading Kobo dictionaries is partially supported (the index is read, the definitions are not, as they are encrypted/obfuscated)
* Reading EPUB (3) dictionaries is not supported; the writing part needs polishing/refactoring
* Reading PRC/MOBI (Kindle) dictionaries is not supported
* There are some limitations on StarDict files that can be read (see comments in `format_stardict.py`)
* Documentation is not complete
* Unit tests are missing


## Acknowledgments 

Many thanks to:

* _uwelovesdonna_ for contributing ideas for improving the code and for setting up many pages of the project wiki;
* _Jens Sadowski_ for pointing out a bug with Unicode file names and for suggesting using multiset `dict()` instead of set `dict()`;
* _oldnat_ for pointing out a bug under Windows and Python 3;
* _Wolfgang Miller-Reichling_ for providing the code for reading CSV dictionaries;
* _branok_ for providing the idea and initial code for German collation function;
* _pal_ for suggesting passing `-l` switch to `MARISA_BUILD`;
* _Lukas Brückner_ for suggesting escaping `& < >` when outputting in XML format;
* _Stephan Lichtenhagen_ for suggesting forcing UTF-8 encoding on Python 3;
* _niconavarrete_ for pointing out the dependency from $CWD (issue #1), solved in v2.0.1;
* _elchamaco_ for providing a StarDict dictionary with a `.syn` file for testing.



