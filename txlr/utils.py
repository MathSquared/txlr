"""Various utility functions."""

import arrow


def lege_year(lege):
    """First year of session. Accurate from 12th Legislature onwards."""
    return 1847 + 2 * lege


def prefiling_date(lege):
    """The first Monday after Election Day; the second Monday in November."""
    return arrow.Arrow(lege_year(lege) - 1, 11, 8).shift(weekday=0)


def convening_date(lege):
    """The second Tuesday in January."""
    return arrow.Arrow(lege_year(lege), 1, 8).shift(weekday=1)


def adjourning_date(lege):
    """The 139th day after the convening date."""
    return convening_date(lege).shift(days=+139)
