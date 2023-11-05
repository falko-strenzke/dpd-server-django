# Django-based word lookup and search in Digital Pali Dictionary

* `cd dpdwebserver`
* `python3 manage.py makemigrations dict`
* `python3 manage.py migrate dict`
* `cd misc/tools/parse-mdict`
* `python3 readmdict.py -b ~/dev/dpd-server-django/dpdwebserver/db.sqlite3 -x /path/to/dpd-mdict.mdx`
* `python3 readmdict.py -b ../../../db.sqlite3 -x ~/Downloads/dpd-2023-08-01/dpd-mdict.mdx`
  * Must provide the main DPD MDict file here.
  * Output will show progress bar and indicated some filtered out entries. May take a few minutes.
  * Afterwards, `db.sqlite3` will be about 2GB large.
* `cd ../../../`
* `python3 manage.py runserver`
* Search page: `http://localhost:8000/dict/dpd/search`
  * Search by substring matches into both headwords and inflected forms, but the results displayed are only the (associated) headwords.
  * Search may fail with error if too many results are returned.
  * No sensible ordering of results.
* Lookup a word: `http://localhost:8000/dict/dpd/lookup/word/sati`
  * Word to lookup after last "/"
  * Unicode characters can be entered directly into the URL

