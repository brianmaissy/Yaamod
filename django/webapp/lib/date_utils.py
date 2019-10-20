from datetime import date
from typing import Optional

from pyluach.hebrewcal import Month, Year
from pyluach.dates import HebrewDate


def to_hebrew_date(gregorian_date: Optional[date], after_sunset: bool):
    if gregorian_date is None:
        return None
    hebrew_date = HebrewDate.from_pydate(gregorian_date)
    if after_sunset:
        hebrew_date += 1
    return hebrew_date


def nth_anniversary_of(original_date, number_of_years):
    original_year = Year(original_date.year)
    anniversary_year = Year(original_date.year + number_of_years)
    anniversary_month = None
    if not original_year.leap and anniversary_year.leap:
        if original_date.month == 12:
            # the original date was in Adar in a regular year, so the
            # anniversary is in Adar Sheni in a leap year
            anniversary_month = Month(anniversary_year.year, 13)
    elif original_year.leap and not anniversary_year.leap:
        if original_date.month == 13:
            # the original date was in Adar Sheni in a leap year, so the
            # anniversary is in Adar in a regular year
            anniversary_month = Month(anniversary_year.year, 12)
    if anniversary_month is None:
        # otherwise, use the same month as in the original year
        anniversary_month = Month(anniversary_year.year, original_date.month)

    if original_date.day > len(anniversary_month):
        # the original date doesn't exist in the anniversary year (either 30
        # Cheshvan, 30 Kislev, or 30 Adar Rishon if the anniversary year is not
        # a leap year), so we go to the first day of the next month
        if anniversary_month.month == 12:
            # the anniversary of 30 Adar Rishon in a non-leap year is the
            # 1st of Nissan
            return HebrewDate(anniversary_month.year, 1, 1)
        else:
            return HebrewDate(anniversary_month.year,
                              anniversary_month.month + 1, 1)
    else:
        return HebrewDate(anniversary_month.year, anniversary_month.month,
                          original_date.day)


def next_anniversary_of(original_date, reference_date=None):
    if reference_date is None:
        reference_date = HebrewDate.today()
    if not reference_date > original_date:
        raise ValueError('reference date must be after original date')
    years_ago = reference_date.year - original_date.year
    next_anniversary = nth_anniversary_of(original_date, years_ago)
    if next_anniversary < reference_date:
        # this is a lot easier than trying to figure out if the N is years_ago
        # or years_ago + 1, because of the leap year edge cases
        next_anniversary = nth_anniversary_of(original_date, years_ago + 1)
    return next_anniversary
