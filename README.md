txlr
====

_Work in progress_

A redirector for the Texas Legislature.

Development setup
-----------------

First, create a file named .env as follows:

```
FLASK_APP=txlr
FLASK_ENV=development
```

Then, run:

```
$ pipenv install
$ pipenv run flask run
```

Usage
-----

Navigate to /go?q=query, where query is whatever query you wish to submit (URL-encoded, of course).
