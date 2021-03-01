"""Various utility functions."""

import arrow


def lege_year(lege):
    """First year of the regular session of the given legislature. Accurate from 12th Legislature onwards."""
    return 1847 + 2 * lege


def year_lege(year):
    """Given the year in which the regular session of a legislature convened or the year after, return the legislature number. Accurate from 1871 onwards."""
    return (year - 1847) // 2


def prefiling_date(lege):
    """The first Monday after Election Day; the second Monday in November. The day on which legislators and legislators-elect may begin to file bills and resolutions for the succeeding session."""
    return arrow.Arrow(lege_year(lege) - 1, 11, 8).shift(weekday=0)


def convening_date(lege):
    """The second Tuesday in January. The constitutional day on which the regular session of the Legislature convenes at noon for its opening day."""
    return arrow.Arrow(lege_year(lege), 1, 8).shift(weekday=1)


def adjourning_date(lege):
    """The 139th day after the convening date. The constitutional day beyond which the regular session of the Legislature cannot continue."""
    return convening_date(lege).shift(days=+139)


def current_lege(date=None, prefiling=False):
    """The current legislative session.

    If date is None, uses the system date and time in Central Time. Otherwise, the date given must be an Arrow object and is converted to Central Time.
    If prefiling is True, the prefiling period is counted as part of the legislative session that is set to convene.

    WARNING: if you create an Arrow object without specifying a time zone, then pass it into this method, it will default to UTC, be changed to the preceding day when it is converted to Central Time, and return results for the day prior to the one you wanted. To fix this, pass tzinfo='US/Central' to the Arrow constructor.
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


def canonicalize(q):
    """Returns the query lowercased and with spaces removed.

    Most queries are case-insensitive and ignore spaces. This function implements this transformation.
    """
    return q.lower().replace(' ', '')


VALID_CODES = [
    'CN',  # Constitution
    'AG',  # Agriculture
    'AL',  # Alcoholic Beverage
    'WL',  # Auxiliary Water Laws
    'BC',  # Business & Commerce
    'BO',  # Business Organizations
    'CP',  # Civil Practice & Remedies
    'CR',  # Criminal Procedure
    'ED',  # Education
    'EL',  # Election
    'ES',  # Estates
    'FA',  # Family
    'FI',  # Finance
    'GV',  # Government (this one's a BIG boi)
    'HS',  # Health & Safety
    'HR',  # Human Resources (conflict with House Resolution)
    'IN',  # Insurance
    'I1',  # Insurance - Not Codified
    'LA',  # Labor
    'LG',  # Local Government
    'NR',  # Natural Resources
    'OC',  # Occupations
    'PW',  # Parks & Wildlife
    'PE',  # Penal
    'PR',  # Property
    'SD',  # Special District Local Laws
    'TX',  # Tax
    'TN',  # Transportation
    'UT',  # Utilities
    'WA',  # Water
    'CV',  # Vernon's Civil Statutes (the uncodified dumpster fire)
]
