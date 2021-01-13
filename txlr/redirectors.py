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
    house_bill,
)
