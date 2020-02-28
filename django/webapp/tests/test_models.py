from datetime import date

from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.test import TestCase
from pyluach.dates import HebrewDate

from webapp.lib.date_utils import nth_anniversary_of, next_anniversary_of
from webapp.models import Synagogue, Person, Yichus, AliyaPrecedenceReason, Gender


class MembersTestCase(TestCase):
    def setUp(self):
        self.synagogue = Synagogue.objects.create(name='Klal Yisrael',
                                                  member_creator=User.objects.create(username='blah'))
        self.father = Person.objects.create(synagogue=self.synagogue, first_name='Dad', gender=Gender.MALE,
                                            date_of_death=date(2018, 11, 11))
        self.mother = Person.objects.create(synagogue=self.synagogue, first_name='Mom', gender=Gender.FEMALE,
                                            date_of_death=date(2017, 3, 3))
        self.sister = Person.objects.create(
            synagogue=self.synagogue, first_name='Sarah', last_name='Levi', gender=Gender.FEMALE, is_member=True,
            date_of_birth=date(1970, 1, 1), father=self.father, mother=self.mother)
        self.brother = Person.objects.create(
            synagogue=self.synagogue, first_name='Shimon', last_name='Levi', gender=Gender.MALE, is_member=True,
            date_of_birth=date(1984, 1, 1), father=self.father, mother=self.mother, yichus=Yichus.LEVI)
        self.wife = Person.objects.create(
            synagogue=self.synagogue, first_name='Rivkah', last_name='Levi', maiden_name='Cohen', gender=Gender.FEMALE,
            is_member=True, date_of_birth=date(1982, 6, 5),
            father=Person.objects.create(first_name='Father in Law', synagogue=self.synagogue),
            mother=Person.objects.create(first_name='Mother in Law', synagogue=self.synagogue))
        self.reuven = Person.objects.create(
            synagogue=self.synagogue, first_name='Reuven', last_name='Levi', gender=Gender.MALE, is_member=True,
            date_of_birth=date(1980, 12, 15), father=self.father, mother=self.mother, wife=self.wife,
            email='reuven@klalyisrael.org.il', phone_number='052-999-9999', address='Gabash',
            yichus=Yichus.LEVI, bar_mitzvah_parasha=12, can_read_haftarah=True)
        self.baby = Person.objects.create(
            synagogue=self.synagogue, first_name='Yitzik', last_name='Levi', gender=Gender.MALE, is_member=True,
            date_of_birth=date(2019, 1, 1), father=self.reuven, mother=self.wife, yichus=Yichus.LEVI)
        self.brother_in_law = Person.objects.create(
            synagogue=self.synagogue, first_name='Moshe', last_name='Cohen', gender=Gender.MALE, is_member=True,
            date_of_birth=date(1978, 2, 1), father=self.wife.father, mother=self.wife.mother, yichus=Yichus.COHEN,
            manual_paternal_name='משה בן שמואל')


class TestSynagogue(MembersTestCase):
    def test_members(self):
        self.assertEquals(self.synagogue.people.count(), 10)

        self.assertEquals(self.synagogue.members.count(), 6)
        self.assertEquals(set(self.synagogue.members.all()), {self.brother, self.sister, self.reuven, self.wife,
                                                              self.brother_in_law, self.baby})

        self.assertEquals(self.synagogue.male_members.count(), 4)
        self.assertEquals(set(self.synagogue.male_members.all()), {self.brother, self.reuven, self.brother_in_law,
                                                                   self.baby})

        self.assertIn(HebrewDate(5780, 7, 1), self.synagogue.get_torah_reading_occasions_table(5780))


class TestPerson(MembersTestCase):
    def test_sanity(self):
        self.assertEquals(self.reuven.full_name, 'Reuven Levi')
        self.assertEquals(str(self.reuven), 'Reuven Levi')
        self.assertEquals(self.father.full_name, 'Dad')
        self.assertEquals(str(self.father), 'Dad')

        self.assertEquals(self.reuven.maiden_name, '')
        self.assertEquals(self.wife.maiden_name, 'Cohen')

        self.assertIsNone(self.reuven.hebrew_date_of_death)
        self.assertEquals(self.reuven.hebrew_date_of_birth, HebrewDate(5741, 10, 8))
        self.assertFalse(self.reuven.is_deceased)

        self.assertIsNone(self.father.hebrew_date_of_birth)
        self.assertEquals(self.father.hebrew_date_of_death, HebrewDate(5779, 9, 3))
        self.assertTrue(self.father.is_deceased)

        self.reuven.email = 'invalid'
        with self.assertRaises(ValidationError):
            self.reuven.clean_fields()

        self.assertEquals(self.reuven.yichus_name, 'Levi')
        self.assertIsNone(self.father.yichus_name)
        self.assertEquals(self.brother_in_law.yichus_name, 'Cohen')

        self.assertIsNone(self.father.paternal_name)
        self.assertEquals(self.reuven.paternal_name, 'Reuven בן Dad')
        self.assertEquals(self.reuven.maternal_name, 'Reuven בן Mom')
        self.assertEquals(self.sister.paternal_name, 'Sarah בת Dad')
        self.assertEquals(self.sister.maternal_name, 'Sarah בת Mom')
        self.assertEquals(self.brother_in_law.paternal_name, 'משה בן שמואל')
        self.assertEquals(self.brother_in_law.maternal_name, 'Moshe בן Mother in Law')

        self.assertTrue(self.reuven.is_married_man)
        self.assertFalse(self.reuven.is_married_woman)
        self.assertTrue(self.reuven.is_married)
        self.assertTrue(self.wife.is_married_woman)
        self.assertFalse(self.wife.is_married_man)
        self.assertTrue(self.wife.is_married)
        self.assertFalse(self.baby.is_married_man)
        self.assertFalse(self.baby.is_married_woman)
        self.assertFalse(self.baby.is_married)

        self.assertEquals(self.reuven.bar_mitzvah_parasha_name, 'Shemos')
        self.assertIsNone(self.brother.bar_mitzvah_parasha_name)

    def test_family_members(self):
        self.assertEquals(self.reuven.father, self.father)
        self.assertEquals(self.reuven.mother, self.mother)
        self.assertIsNone(self.father.mother)
        self.assertEquals(self.reuven.wife, self.wife)
        self.assertEquals(self.reuven.wife.husband, self.reuven)
        self.assertIsNone(self.brother.wife)

        children = {self.reuven, self.brother, self.sister}
        self.assertEquals(set(self.father.children.all()), children)
        self.assertEquals(set(self.father.children_of_father.all()), children)
        self.assertEquals(set(self.father.children_of_mother.all()), set())
        self.assertEquals(set(self.mother.children.all()), children)
        self.assertEquals(set(self.mother.children_of_father.all()), set())
        self.assertEquals(set(self.mother.children_of_mother.all()), children)
        self.assertFalse(self.brother.children.exists())

        self.assertEquals(self.father.immediate_family_members, children)
        self.assertEquals(self.mother.immediate_family_members, children)
        self.assertEquals(self.reuven.immediate_family_members, {self.mother, self.father, self.brother, self.sister,
                                                                 self.wife, self.baby})
        self.assertEquals(self.brother.immediate_family_members, {self.mother, self.father, self.sister, self.reuven})
        self.assertEquals(self.baby.immediate_family_members, {self.reuven, self.wife})
        self.assertEquals(self.wife.immediate_family_members,  {self.wife.mother, self.wife.father, self.reuven,
                                                                self.brother_in_law, self.baby})
        self.assertEquals(self.brother_in_law.immediate_family_members, {self.wife.mother, self.wife.father, self.wife})

    def test_can_get_aliya(self):
        self.assertEquals(self.reuven.bar_mitzvah_date, nth_anniversary_of(self.reuven.hebrew_date_of_birth, 13))
        self.assertTrue(self.reuven.is_bar_mitzvah)
        self.assertTrue(self.reuven.can_get_aliya)
        self.reuven.cannot_get_aliya = True
        self.reuven.save()
        self.assertFalse(self.reuven.can_get_aliya)
        self.reuven.cannot_get_aliya = False
        self.reuven.save()
        self.assertTrue(self.reuven.can_get_aliya)
        self.reuven.date_of_death = date.today()
        self.reuven.save()
        self.assertFalse(self.reuven.can_get_aliya)

        self.assertFalse(self.baby.is_bar_mitzvah)
        self.assertFalse(self.baby.can_get_aliya)

        self.assertIsNone(self.wife.bar_mitzvah_date)
        self.assertFalse(self.wife.is_bar_mitzvah)
        self.assertFalse(self.wife.can_get_aliya)


class TestAliyaPrecedence(MembersTestCase):
    def test_yahrzeit_aliya(self):
        yahrzeit = next_anniversary_of(self.reuven.father.hebrew_date_of_death, HebrewDate(5780, 8, 1))
        self.assertEquals(yahrzeit, HebrewDate(5780, 9, 3))
        self.assertFalse(self.reuven.needs_yahrzeit_aliya(HebrewDate(5780, 8, 1)))
        self.assertFalse(self.reuven.needs_yahrzeit_aliya(yahrzeit - 2))
        # the shabbat before
        self.assertTrue(self.reuven.needs_yahrzeit_aliya(yahrzeit - 1))
        # the day of
        self.assertTrue(self.reuven.needs_yahrzeit_aliya(yahrzeit))
        self.assertFalse(self.reuven.needs_yahrzeit_aliya(yahrzeit + 1))

        # has no yahrzeits defined
        self.assertFalse(self.brother_in_law.needs_yahrzeit_aliya(HebrewDate(5780, 9, 3)))

    def test_birthday_aliya(self):
        birthday = next_anniversary_of(self.reuven.hebrew_date_of_birth, HebrewDate(5780, 10, 1))
        self.assertEquals(birthday, HebrewDate(5780, 10, 8))  # this is a Sunday
        self.assertFalse(self.reuven.needs_birthday_aliya(birthday - 7))
        self.assertFalse(self.reuven.needs_birthday_aliya(birthday - 2))
        self.assertFalse(self.reuven.needs_birthday_aliya(birthday + 6))
        # shabbat before
        self.assertTrue(self.reuven.needs_birthday_aliya(birthday - 1))
        # actual birthday
        self.assertTrue(self.reuven.needs_birthday_aliya(birthday))

    def test_bar_mitzvah_parasha_shabbat(self):
        self.assertFalse(self.reuven.is_bar_mitzvah_parasha_shabbat(HebrewDate(5780, 9, 2)))
        # the day before the shabbat
        self.assertFalse(self.reuven.is_bar_mitzvah_parasha_shabbat(HebrewDate(5780, 10, 20)))
        # the shabbat itself
        self.assertTrue(self.reuven.is_bar_mitzvah_parasha_shabbat(HebrewDate(5780, 10, 21)))
        # the day after
        self.assertFalse(self.reuven.is_bar_mitzvah_parasha_shabbat(HebrewDate(5780, 10, 22)))
        # has no bar mitzvah parasha defined
        self.assertFalse(self.brother.is_bar_mitzvah_parasha_shabbat(HebrewDate(5780, 10, 21)))

    def test_aliya_precedence(self):
        self.assertEquals(self.reuven.get_aliya_precedence(HebrewDate(5780, 10, 21)),
                          AliyaPrecedenceReason.BAR_MITZVAH_PARASHA)
        self.assertEquals(self.brother.get_aliya_precedence(HebrewDate(5780, 10, 21)),
                          AliyaPrecedenceReason.BIRTHDAY)
        self.assertIsNone(self.brother.get_aliya_precedence(HebrewDate(5780, 11, 1)))
        self.assertEquals(self.reuven.get_aliya_precedence(HebrewDate(5780, 9, 2)), AliyaPrecedenceReason.YAHRZEIT)
        self.assertEquals(self.brother.get_aliya_precedence(HebrewDate(5780, 9, 2)), AliyaPrecedenceReason.YAHRZEIT)
        self.assertIsNone(self.brother_in_law.get_aliya_precedence(HebrewDate(5780, 9, 2)))

    def test_suggested_olim(self):
        self.brother.last_aliya_date = date(2019, 12, 7)
        self.brother.save()
        self.reuven.last_aliya_date = date(2019, 11, 2)
        self.reuven.save()

        self.assertEquals(self.synagogue.get_olim(HebrewDate(5780, 10, 21)), [
            (self.brother, AliyaPrecedenceReason.BIRTHDAY),
            (self.reuven, AliyaPrecedenceReason.BAR_MITZVAH_PARASHA),
            (self.brother_in_law, None)
        ])

        self.assertEquals(self.synagogue.get_olim(HebrewDate(5780, 9, 2)), [
            (self.reuven, AliyaPrecedenceReason.YAHRZEIT),
            (self.brother, AliyaPrecedenceReason.YAHRZEIT),
            (self.brother_in_law, None)
        ])

        olim = self.synagogue.get_olim(HebrewDate(5780, 11, 15))
        self.assertEquals(olim, [
            (self.brother_in_law, None),
            (self.reuven, None),
            (self.brother, None),
        ])
        # check last aliya dates
        assert olim[0][0].last_aliya_date is None
        assert olim[0][0].last_aliya_hebrew_date is None
        assert olim[1][0].last_aliya_date == date(2019, 11, 2)
        assert olim[1][0].last_aliya_hebrew_date == HebrewDate(5780, 8, 4)
        assert olim[2][0].last_aliya_date == date(2019, 12, 7)
        assert olim[2][0].last_aliya_hebrew_date == HebrewDate(5780, 9, 9)
