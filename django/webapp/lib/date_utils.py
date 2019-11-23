from contextlib import suppress
from datetime import date
from functools import lru_cache
from itertools import chain
from typing import Optional, NamedTuple, Dict

from pyluach.dates import HebrewDate
from pyluach.hebrewcal import Month, Year, _adjust_postponed
from pyluach.parshios import parshatable


def to_hebrew_date(gregorian_date: Optional[date], after_sunset: bool) -> Optional[HebrewDate]:
    if gregorian_date is None:
        return None
    hebrew_date = HebrewDate.from_pydate(gregorian_date)
    if after_sunset:
        hebrew_date += 1
    return hebrew_date


def nth_anniversary_of(original_date: HebrewDate, number_of_years: int) -> HebrewDate:
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


def next_anniversary_of(original_date: HebrewDate, reference_date: Optional[HebrewDate] = None) -> HebrewDate:
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


def next_reading_of_parasha(parasha_number: int, reference_date: Optional[HebrewDate] = None,
                            israel: bool = True) -> HebrewDate:
    if reference_date is None:
        reference_date = HebrewDate.today()
    this_year_table = parshatable(reference_date.year, israel=israel)
    next_year_table = parshatable(reference_date.year + 1, israel=israel)
    for shabbat_date, parasha_numbers in chain(this_year_table.items(), next_year_table.items()):
        if shabbat_date >= reference_date and parasha_numbers is not None and parasha_number in parasha_numbers:
            return shabbat_date


class TorahReadingOccasion(NamedTuple):
    description: str
    shacharit_aliyot: int
    mincha_aliyot: int = 0

    @property
    def has_maftir(self) -> bool:
        # has a maftir aliya in addition to the regular ones
        return self.shacharit_aliyot >= 5


@lru_cache(50)
def make_torah_reading_occasions_table(year: int, israel: bool, jerusalem: bool) -> Dict[HebrewDate,
                                                                                         TorahReadingOccasion]:
    # TODO: possible improvements:
    #  - add descriptions in hebrew
    #  - make the descriptions include more information (month for rosh chodesh, parasha for shabbat, and intersection
    #        of multiple occasions, like shabbat rosh chodesh, shabbat purim, rosh chodesh chanukah, four parshiot)
    #  - add descriptions of the aliyot (especially maftir)
    #  - include days with haftarah but no maftir
    #  - include mondays and thursdays
    table = {}

    # holidays
    table[HebrewDate(year, 7, 1)] = TorahReadingOccasion('Rosh Hashana', 5)
    table[HebrewDate(year, 7, 2)] = TorahReadingOccasion('Rosh Hashana', 5)
    table[HebrewDate(year, 7, 10)] = TorahReadingOccasion('Yom Kippur', 6, 3)
    table[HebrewDate(year, 7, 15)] = TorahReadingOccasion('Sukkot', 5)
    if israel:
        table[HebrewDate(year, 7, 16)] = TorahReadingOccasion('Chol Hamoed Sukkot', 4)
    else:
        table[HebrewDate(year, 7, 16)] = TorahReadingOccasion('Sukkot', 5)
    table[HebrewDate(year, 7, 17)] = TorahReadingOccasion('Chol Hamoed Sukkot', 4)
    table[HebrewDate(year, 7, 18)] = TorahReadingOccasion('Chol Hamoed Sukkot', 4)
    table[HebrewDate(year, 7, 19)] = TorahReadingOccasion('Chol Hamoed Sukkot', 4)
    table[HebrewDate(year, 7, 20)] = TorahReadingOccasion('Chol Hamoed Sukkot', 4)
    table[HebrewDate(year, 7, 21)] = TorahReadingOccasion('Chol Hamoed Sukkot', 4)
    table[HebrewDate(year, 7, 22)] = TorahReadingOccasion('Shmini Atzeret', 5)
    if not israel:
        table[HebrewDate(year, 7, 23)] = TorahReadingOccasion('Simchat Torah', 5)

    for day in (HebrewDate(year, 9, 25) + i for i in range(8)):
        table[day] = TorahReadingOccasion('Chanukah', 3)

    purim_month = 13 if Year(year).leap else 12
    purim_date = HebrewDate(year, purim_month, 15 if jerusalem else 14)
    if not purim_date.shabbos():
        table[purim_date] = TorahReadingOccasion('Shushan Purim' if jerusalem else 'Purim', 3)

    table[HebrewDate(year, 1, 15)] = TorahReadingOccasion('Pesach', 5)
    if israel:
        table[HebrewDate(year, 1, 16)] = TorahReadingOccasion('Chol Hamoed Pesach', 4)
    else:
        table[HebrewDate(year, 1, 16)] = TorahReadingOccasion('Pesach', 5)
    table[HebrewDate(year, 1, 17)] = TorahReadingOccasion('Chol Hamoed Pesach', 4)
    table[HebrewDate(year, 1, 18)] = TorahReadingOccasion('Chol Hamoed Pesach', 4)
    table[HebrewDate(year, 1, 19)] = TorahReadingOccasion('Chol Hamoed Pesach', 4)
    table[HebrewDate(year, 1, 20)] = TorahReadingOccasion('Chol Hamoed Pesach', 4)
    table[HebrewDate(year, 1, 21)] = TorahReadingOccasion('Pesach', 5)
    if not israel:
        table[HebrewDate(year, 1, 22)] = TorahReadingOccasion('Pesach', 5)

    table[HebrewDate(year, 3, 6)] = TorahReadingOccasion('Shavuot', 5)
    if not israel:
        table[HebrewDate(year, 3, 7)] = TorahReadingOccasion('Shavuot', 5)

    # rosh chodesh (overrides other occasions)
    for month in range(1, 14):
        if month == 7:
            # Rosh Hashana
            continue
        with suppress(ValueError):
            table[HebrewDate(year, month, 1)] = TorahReadingOccasion('Rosh Chodesh', 4)
        with suppress(ValueError):
            table[HebrewDate(year, month, 30)] = TorahReadingOccasion('Rosh Chodesh', 4)

    # shabbat (overrides other occasions)
    shabbat = HebrewDate(year, 7, 1).shabbos()
    while shabbat.year == year:
        table[shabbat] = TorahReadingOccasion('Shabbat', 7, 3)
        shabbat += 7

    # fast days
    table[_adjust_postponed(HebrewDate(year, 7, 3))] = TorahReadingOccasion('Tzom Gedalia', 3, 3)
    table[_adjust_postponed(HebrewDate(year, 10, 10))] = TorahReadingOccasion('10 of Tevet', 3, 3)
    table[_adjust_postponed(HebrewDate(year, purim_month, 13))] = TorahReadingOccasion('Taanit Esther', 3, 3)
    table[_adjust_postponed(HebrewDate(year, 4, 17))] = TorahReadingOccasion('17 of Tamuz', 3, 3)
    table[_adjust_postponed(HebrewDate(year, 5, 9))] = TorahReadingOccasion('9 of Av', 3, 3)

    return table
