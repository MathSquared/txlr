"""Functions to convert queries to redirected URLs.

The handler for the go route passes the query to each of these redirector functions. (Cookie parsing will be added later.)

Redirectors should not have side effects.

Each redirector must return one of three things:
- the tuple (True, url), where url is the address to which to redirect the query;
- the tuple (False, None), indicating that the redirector is not relevant to the query; or
- the tuple (False, msg), where msg is an error to be displayed to the user.

Each redirector may have any of the following attributes:
- title, a string (initial lowercase) with a short description of the redirector's function.
- pattern, a string with an arbitrary representation of the queries to which the redirector is relevant. In other words, a query that fits the pattern will most likely not return (False, None).

Each redirector is added to the REDIRECTORS tuple in this module. If one or more redirectors returns a tuple whose first member is True, the client is sent to the URL returned by the redirector first on the REDIRECTORS list. Otherwise, all of the error messages returned by redirectors are returned along with the title and pattern of each redirector returning the message.

"""


import re

from . import utils
from .utils import canonicalize


# A word on security.
#
# In theory, txlr cannot cause a user security harm that they did not wreak on themselves, because txlr only deterministically transforms the user's input and redirects them to a website determined by their input.
#
# In practice, we want a user to be confident that any txlr link they go to will be benign, regardless of what's in the query string. Also, it is especially problematic if txlr calls out to external services; a malicious client could then cause txlr to make an unwanted call to that service, or a compromised service could influence txlr's redirections. Calling to an external service also introduces an extra point of failure and introduces the possibility of side effects.
#
# Therefore:
# - A redirector must not make a request to an external service. (To be clear, returning a URL to be redirected to does not constitute making a request; that is the entire point of txlr. The difference is that the client, not txlr, is making the request.)
# - A redirector must sanitize the query it receives and refuse to process a query that does not meet the expected pattern.
# - Similarly, a redirector must treat the content of cookies as untrusted. If a cookie does not contain an expected value, a redirector must ignore the cookie.
# - If a redirector produces an error message, that message must not contain untrusted user input. This means if any element of the query or a cookie is included in an error message, it must have been sanitized first. As a corollary, if a redirector produces an error because it encounters an unclean query or cookie, it must not include the query or cookie in its error message.
#
# These rules will ensure that txlr queries are fast, secure, and reliable.


def statute(q):
    q = canonicalize(q)
    # Liberal pattern because of janky queries like 6-1/2 and 4413(47e-1)
    PAT = '([a-z0-9]{2})([A-Za-z0-9._/()-]+)'
    m = re.fullmatch(PAT, q)
    if m:
        code = m.group(1).upper()
        section = m.group(2)

        if code not in utils.VALID_CODES:
            return (False, 'The code of law you gave is invalid')

        # Link construction: https://statutes.capitol.texas.gov/LinksFAQ.aspx
        # We build links directly because we want to support subchapters (101.B), which GetStatute won't recognize.
        url = 'https://statutes.capitol.texas.gov/docs/{code}/htm/{code}.{chapter}.htm#{anchor}'
        chapter = ''
        anchor = ''

        if code == 'CV':
            # For civil statutes, we can search by title.chapter or by article
            if '.' in section:
                # title.chapter
                section = section.upper()
                if re.fullmatch('[A-Z0-9]+[.][A-Z0-9_/-]+', section):
                    chapter = section.replace('/', '_')  # Title 71, Chapter 6-1/2, Abortion
                else:
                    return (False, 'The Civil Statutes chapter number you gave is invalidly formatted')
            else:
                # article
                # Let's just trust them on the article number bc Vernon's is a shitshow
                chapter = section
                # TODO I thought GetStatute worked for types other than Word...?
                url = 'https://statutes.capitol.texas.gov/GetStatute.aspx?DocumentType=Word&Value={code}.{chapter}'
        else:
            section = section.upper()

            # Some checks on the section to make sure it's a decent section
            if not re.fullmatch('[0-9][A-Z0-9-]*([.][A-Z0-9-]*)?', section):
                return (False, 'The code section number you gave is invalidly formatted; it must start with a number and contain alphanumeric characters, dashes, and at most one decimal point')

            # We can search by chapter (article for the Constitution), section, or subchapter
            # A dot can precede nothing to indicate a chapter search alone,
            # so for this test we ignore a dot in the final position
            if '.' in section[:-1]:
                # chapter.section or chapter.subchapter
                # Subchapters begin with letters
                predot, postdot = section.split('.', 1)
                if postdot[0].isalpha():
                    chapter = predot
                    anchor = postdot
                else:
                    chapter = predot
                    anchor = section
            else:
                if section[-1] == '.':
                    section = section[:-1]
                chapter = section

        return (True, url.format(code=code, chapter=chapter, anchor=anchor))
    else:
        return (False, None)
statute.title = 'Constitution and statutes'
statute.pattern = '<code><chapter>[.[<section|subchapter>]], cn<article>.<section>, cv<title>.<chapter>, cv<article>'


def statute_toc(q):
    q = canonicalize(q).upper()
    if q in utils.VALID_CODES:
        return (True, 'https://statutes.capitol.texas.gov/?link={}'.format(q))
    elif len(q) == 2:
        return (False, 'The code of law you provided is not valid')
    else:
        return (False, None)
statute_toc.title = 'Constitution and statutes, code table of contents'
statute_toc.pattern = '<code>'


def house_bill(q):
    # This will be written more robustly Soon(tm).
    if q.isascii() and len(q) >= 3 and q[0] in 'hH' and q[1] in 'bB' and q[2:].isdigit():
        num = q[2:]
        return (True, 'https://capitol.texas.gov/BillLookup/History.aspx?LegSess=87R&Bill=HB{}'.format(num))
    else:
        return (False, None)
house_bill.title = 'House bill, by number'
house_bill.pattern = 'hb<number>'


REDIRECTORS = (
    statute,
    house_bill,
)
