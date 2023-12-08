# Django-based word lookup and search in Digital Pali Dictionary

* `cd dpdwebserver`
* `python3 manage.py makemigrations dict`
* `python3 manage.py migrate dict`
* `cd misc/tools/parse-mdict`
* `python3 readmdict.py -b ../../../db.sqlite3 -x /path/to/dpd-mdict.mdx`
  * Must provide the main DPD MDict file here.
  * Output will show progress bar and indicated some filtered out entries. May take a few minutes.
  * Afterwards, `db.sqlite3` will be about 2GB large.
* `cd ../../../`
* `python3 manage.py runserver`
* Search page: `http://localhost:8000/dict/dpd/search`
  * Search by substring matches into both headwords and inflected forms, but the results displayed are only the (associated) headwords.
  * Search may fail with error if too many results are returned.
  * No sensible ordering of results.
* Lookup a word: `http://localhost:8000/dict/dpd/lookup/sati`
  * Word to lookup after ".../lookup/"
  * Unicode characters can be entered directly into the URL

  
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
    * and enable spell checking in Vim: `set spell spelllang=en,pi` to have both english and and Pāḷi words recognized
    * caveats: neither vowel lengthening before *'ti* nor sandhis written with "'" which change of the first word's final consonant are recognized
