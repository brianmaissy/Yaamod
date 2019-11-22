from datetime import date
from unittest import TestCase

from pyluach.dates import HebrewDate
from pyluach.hebrewcal import Year, holiday

from webapp.lib.date_utils import to_hebrew_date, nth_anniversary_of, next_anniversary_of, next_reading_of_parasha, \
    make_torah_reading_occasions_table


class TestHebrewDate(TestCase):
    def test_hebrew_date(self):
        self.assertEquals(to_hebrew_date(None, False), None)
        self.assertEquals(to_hebrew_date(date(1989, 11, 28), False), HebrewDate(5750, 8, 30))
        self.assertEquals(to_hebrew_date(date(1989, 11, 28), True), HebrewDate(5750, 9, 1))


class TestNthAnniversaryOf(TestCase):
    def test_adar_bar_mitzvah_paradox(self):
        older_kids_birthday = HebrewDate(5746, 12, 16)
        younger_kids_birthday = HebrewDate(5746, 13, 2)
        older_kids_bar_mitzvah = nth_anniversary_of(older_kids_birthday, 13)
        self.assertEquals(older_kids_bar_mitzvah, HebrewDate(5759, 12, 16))
        younger_kids_bar_mitzvah = nth_anniversary_of(younger_kids_birthday, 13)
        self.assertEquals(younger_kids_bar_mitzvah, HebrewDate(5759, 12, 2))
        self.assertLess(older_kids_birthday, younger_kids_birthday)
        self.assertGreater(older_kids_bar_mitzvah, younger_kids_bar_mitzvah)

    def test_adar_anniversary_in_leap_year(self):
        original_date = HebrewDate(5745, 12, 16)
        first_anniversary = HebrewDate(5746, 13, 16)
        self.assertEquals(nth_anniversary_of(original_date, 1), first_anniversary)

    def test_anniversary_of_30_adar_rishon(self):
        original_date = HebrewDate(5746, 12, 30)
        first_anniversary = HebrewDate(5759, 1, 1)
        self.assertEquals(nth_anniversary_of(original_date, 13), first_anniversary)

    def test_anniversary_of_30_cheshvan(self):
        date_of_birth = HebrewDate(5750, 8, 30)
        self.assertEquals(nth_anniversary_of(date_of_birth, 1), HebrewDate(5751, 9, 1))
        self.assertEquals(nth_anniversary_of(date_of_birth, 2), HebrewDate(5752, 8, 30))


class TestNextAnniversaryOf(TestCase):
    def test_next_anniversary_invalid_reference_date(self):
        original_date = HebrewDate(5750, 8, 1)
        with self.assertRaises(ValueError):
            next_anniversary_of(original_date, original_date - 1)
        with self.assertRaises(ValueError):
            next_anniversary_of(original_date, original_date)
        self.assertEquals(next_anniversary_of(original_date, original_date + 1), HebrewDate(5751, 8, 1))

    def test_next_anniversary_is_today(self):
        original_date = HebrewDate(5750, 8, 1)
        reference_date = HebrewDate(5751, 8, 1)
        self.assertEquals(next_anniversary_of(original_date, reference_date), reference_date)

    def test_next_anniversary_is_tomorrow(self):
        original_date = HebrewDate(5750, 8, 1)
        next_anniversary = HebrewDate(5751, 8, 1)
        self.assertEquals(next_anniversary_of(original_date, next_anniversary - 1), next_anniversary)

    def test_next_anniversary_is_a_year_from_yesterday(self):
        original_date = HebrewDate(5750, 8, 1)
        next_anniversary = HebrewDate(5751, 8, 1)
        self.assertEquals(next_anniversary_of(original_date, original_date + 1), next_anniversary)


class TestNextReadingOfParasha(TestCase):
    def test_next_reading_is_today(self):
        self.assertEquals(next_reading_of_parasha(2, HebrewDate(5780, 8, 11)), HebrewDate(5780, 8, 11))

    def test_next_reading_is_this_shabbat(self):
        self.assertEquals(next_reading_of_parasha(2, HebrewDate(5780, 8, 5)), HebrewDate(5780, 8, 11))

    def test_next_reading_is_later_this_year(self):
        self.assertEquals(next_reading_of_parasha(2, HebrewDate(5780, 7, 5)), HebrewDate(5780, 8, 11))

    def test_next_reading_is_next_year(self):
        self.assertEquals(next_reading_of_parasha(2, HebrewDate(5780, 8, 12)), HebrewDate(5781, 8, 13))

    def test_double_parasha(self):
        self.assertEquals(next_reading_of_parasha(21, HebrewDate(5780, 8, 1)),
                          next_reading_of_parasha(21, HebrewDate(5780, 8, 1)))


class TestTorahReadingOccasions(TestCase):
    def test_occasions(self):
        for year in (5779, 5780):
            for israel in (True, False):
                number_of_shabbatot = 0
                rosh_chodesh_months = []
                holidays_count = 0
                for day, occasion in make_torah_reading_occasions_table(year, israel).items():
                    if holiday(day, israel):
                        holidays_count += 1
                    if day.weekday() == 7:
                        self.assertEquals(occasion.shacharit_aliyot, 7)
                        self.assertEquals(occasion.mincha_aliyot, 3)
                        number_of_shabbatot += 1
                    if day.day in (1, 30):
                        if not holiday(day, israel) and day.weekday() != 7:
                            self.assertEquals(occasion.shacharit_aliyot, 4)
                            self.assertEquals(occasion.mincha_aliyot, 0)
                        rosh_chodesh_months.append(day.month)

                expected_number_of_shabbatot = 0
                shabbat = HebrewDate(year, 7, 1).shabbos()
                while shabbat.year == year:
                    expected_number_of_shabbatot += 1
                    shabbat += 7

                self.assertEquals(number_of_shabbatot, expected_number_of_shabbatot)
                self.assertEquals(len(set(rosh_chodesh_months)), 13 if Year(year).leap else 12)
                self.assertEquals(holidays_count, 32 if israel else 35)
