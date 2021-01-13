"""Various utility functions."""

import arrow


def lege_year(lege):
    """First year of session. Accurate from 12th Legislature onwards."""
    return 1847 + 2 * lege


def year_lege(year):
    """Given the year in which the regular session of a legislature convened or the year after, return the legislature number. Accurate from 1871 onwards."""
    return (year - 1847) // 2


def prefiling_date(lege):
    """The first Monday after Election Day; the second Monday in November."""
    return arrow.Arrow(lege_year(lege) - 1, 11, 8).shift(weekday=0)


def convening_date(lege):
    """The second Tuesday in January."""
    return arrow.Arrow(lege_year(lege), 1, 8).shift(weekday=1)


def adjourning_date(lege):
    """The 139th day after the convening date."""
    return convening_date(lege).shift(days=+139)


def current_lege(date=None, prefiling=False):
    """The current legislative session.

    If date is None, uses the system date and time in Central Time. Otherwise, the date given must be an Arrow object and is converted to Central Time.
    If prefiling is True, the prefiling period is counted as part of the legislative session that is set to convene.
    """
    if date is None:
        date = arrow.now('US/Central')
    else:
        date = date.to('US/Central')

    base = year_lege(date.year)

    # In odd years, the Legislature might have yet to convene
    if date.year % 2 != 0:
        if prefiling:
            return base
        else:
            convene = convening_date(base)
            if date < convene:
                return base - 1
            else:
                return base
    # In even years, prefiling for the next legislature might have begun
    else:
        if not prefiling:
            return base
        else:
            prefile = prefiling_date(base + 1)
            if date >= prefile:
                return base + 1
            else:
                return base
