# Django-based server for word lookup and search in Digital Pāḷi Dictionary

This project implements a Django-based webserver that allows word lookup and search in the [Digital Pāḷi Dictionary](https://digitalpalidictionary.github.io/) (DPD). For the purpose of building the underlying database, the MDict release files of the DPD and the [dpd-db](https://github.com/digitalpalidictionary/dpd-db) are used.
An instance is running at [http://niyamata.de](https://digitalpalidictionary.github.io/).

* `cd dpdwebserver`
* `python3 manage.py makemigrations dict`
* `python3 manage.py migrate dict`
* `cd misc/tools/parse-mdict`
* `python3 readmdict.py -b ../../../db.sqlite3 -x /path/to/dpd-mdict.mdx`
  * Must provide the main DPD MDict file here.
  * Output will show progress bar and indicated some filtered out entries. May take a few minutes.
  * Afterwards, the `db.sqlite3` file will be about 2GB large.
* Build and extract information from dpd-db:
  * clone [dpd-db](https://github.com/digitalpalidictionary/dpd-db) and build the `dpd.db` according to the instructions in [README.md](https://github.com/digitalpalidictionary/dpd-db/blob/main/README.md)
  * `cd misc/tools/dpd-db-extractor`
  * create a configuration file based on the `sample-config.ini` for use in the next command and set the properties:
    * `source_db` to the `dpd.db` file the was build in the previous step
    * `target_db` to the `db.sqlite3`  file (see above)
  * run the command `./dpd-db-extractor.py --config=<config-file-name>`
  * this will fill the table with the construction elements that is needed for the construction-based search
* Optionally add the DPD grammar and deconstructor supplementary dictionaries:
  * `python3 readmdict.py -b ../../../db.sqlite3 -x /path/to/dpd-grammar-mdict.mdx`
  * `python3 readmdict.py -b ../../../db.sqlite3 -x /path/to/dpd-deconstructor-mdict.mdx`
  * Now the resulting `db.sqlite3` file will be about 4.5 GB large.
  * Note that the file names `dpd-grammar-mdict.mdx` and `dpd-deconstructor-mdict.mdx` are used to determine which type of supplementary dictionary is being processed based on the presence of the substrings "grammar" and "deconstructor".
  Thus do not change the file names.
* `cd ../../../`
* `python3 manage.py runserver`
* Search page: `http://localhost:8000/dict/dpd/search`
  * Search by substring matches into both headwords and inflected forms, but the results displayed are only the (associated) headwords.
  * No sensible ordering of results.
* Lookup a word: `http://localhost:8000/dict/dpd/lookup/sati`
  * Word to lookup after ".../lookup/"
  * Unicode characters can usually be entered directly into the URL


## Tools

### readmdict.py

Can be used to build from the MDict version of the DPD

* an sqlite3 database (see above),
* a word list to build a dictionary file for applications
  * e.g. for vim:
    * `python3 readmdict.py -w dpd-word-list.txt -x /path/to/dpd-mdict.mdx`
    * the above command creates the file `dpd-word-list.txt`
    * in Vim run `:mkspell pi.utf-8.spl dpd-word-list.txt`
    * then place the file `pi.utf-8.spl` into `~/.vim/spell`
    * and enable spell checking in Vim: `set spell spelllang=en,pi` to have both English and Pāḷi words recognized
    * caveats: neither vowel lengthening before *'ti* nor sandhis written with "'" which change of the first word's final consonant are recognized

### dpd-db-extractor.py

This tool extracts information from the DPD data base to fill additional tables for the the construction-based search, see above.
