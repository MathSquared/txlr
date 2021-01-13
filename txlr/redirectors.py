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


REDIRECTORS = (
)