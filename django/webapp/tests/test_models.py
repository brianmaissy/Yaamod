from datetime import date

from django.contrib.auth.models import Group, User
from django.test import TestCase
from pyluach.dates import HebrewDate

from webapp.lib.date_utils import nth_anniversary_of, next_anniversary_of
from webapp.models import Synagogue, Person, Member, MaleMember, Yichus, AliyaPrecedenceReason


def make_synagogue():
    admins = Group.objects.create(name='admins')
    return Synagogue.objects.create(name='Klal Yisrael', admins=admins,
                                    member_creator=User.objects.create(username='admin'))


class MembersTestCase(TestCase):
    def setUp(self):
        today = date.today()
        self.synagogue = make_synagogue()
        self.father = Person.objects.create(formal_name='Dad', synagogue=self.synagogue)
        self.mother = Person.objects.create(formal_name='Mom', synagogue=self.synagogue)
        self.daughter = Member.objects.create(
            formal_name='Sarah', synagogue=self.synagogue, last_name='Levi', date_of_birth=date(2019, 1, 1),
            father=self.father, mother=self.mother)
        self.son = MaleMember.objects.create(
            formal_name='Reuven', synagogue=self.synagogue, last_name='Levi', date_of_birth=today,
            father=self.father, mother=self.mother, yichus=Yichus.LEVI)
        self.wife = Member.objects.create(
            formal_name='Rivkah', synagogue=self.synagogue, last_name='Shtern', date_of_birth=today,
            father=Person.objects.create(formal_name='Father in Law', synagogue=self.synagogue),
            mother=Person.objects.create(formal_name='Mother in Law', synagogue=self.synagogue))


class TestSynagogue(MembersTestCase):
    def test_members(self):
        self.assertEquals(self.synagogue.person_set.count(), 7)
        self.assertEquals(self.synagogue.member_set.count(), 3)
        self.assertEquals(set(self.synagogue.member_set.all()), {self.daughter, self.son.member_ptr, self.wife})
        for member in self.synagogue.member_set.all():
            self.assertIsInstance(member, Member)


class TestPerson(MembersTestCase):
    def test_sanity(self):
        self.assertEquals(str(self.father), 'Dad')
        self.assertIsNone(self.father.hebrew_date_of_death)
        self.father.date_of_death = date(2019, 1, 1)
        self.daughter.save()
        self.assertEquals(self.father.hebrew_date_of_death, HebrewDate(5779, 10, 24))

    def test_children(self):
        children = {self.son.member_ptr, self.daughter}
        self.assertEquals(set(self.father.children.all()), children)
        self.assertEquals(set(self.father.children_of_father.all()), children)
        self.assertEquals(set(self.father.children_of_mother.all()), set())
        self.assertEquals(set(self.mother.children.all()), children)
        self.assertEquals(set(self.mother.children_of_father.all()), set())
        self.assertEquals(set(self.mother.children_of_mother.all()), children)

        self.assertFalse(self.son.children.exists())


class TestMember(MembersTestCase):
    def test_sanity(self):
        self.assertEquals(self.daughter.first_name, 'Sarah')
        self.assertEquals(self.daughter.full_name,  'Sarah Levi')
        self.assertEquals(str(self.daughter),  'Sarah Levi')
        self.daughter.manual_first_name = 'Sarai'
        self.daughter.save()
        self.assertEquals(self.daughter.first_name, 'Sarai')
        self.assertEquals(self.daughter.full_name,  'Sarai Levi')
        self.assertEquals(str(self.daughter),  'Sarai Levi')

        self.assertFalse(self.daughter.is_male)
        self.assertEquals(self.daughter.hebrew_date_of_birth, HebrewDate(5779, 10, 24))

        self.assertIn(self.daughter, self.daughter.father.children.all())
        self.assertIn(self.daughter, self.daughter.mother.children.all())

    def test_full_formal_names(self):
        self.assertEquals(self.son.paternal_formal_name, 'Reuven בן Dad')
        self.assertEquals(self.son.maternal_formal_name, 'Reuven בן Mom')
        self.assertEquals(self.daughter.paternal_formal_name, 'Sarah בת Dad')
        self.assertEquals(self.daughter.maternal_formal_name, 'Sarah בת Mom')


class TestMaleMember(MembersTestCase):
    def test_sanity(self):
        self.assertEquals(self.son.yichus, Yichus.LEVI)
        self.assertEquals(self.son.yichus_name, 'Levi')

        self.assertIsNone(self.son.bar_mitzvah_parasha)
        self.assertIsNone(self.son.bar_mitzvah_parasha_name)
        self.son.bar_mitzvah_parasha = 0
        self.assertEquals(self.son.bar_mitzvah_parasha_name, 'Beraishis')

        self.assertIsInstance(self.son.member_ptr, Member)
        self.son_as_member = Member.objects.get(id=self.son.id)
        self.assertIsInstance(self.son_as_member, Member)
        self.assertIsInstance(self.son_as_member.male_member, MaleMember)

    def test_can_get_aliya(self):
        self.assertEquals(self.son.bar_mitzvah_date, nth_anniversary_of(self.son.hebrew_date_of_birth, 13))
        self.assertFalse(self.son.is_bar_mitzvah)
        self.assertFalse(self.son.can_get_aliya)

        self.son.date_of_birth = self.son.date_of_birth.replace(year=self.son.date_of_birth.year - 14)
        self.son.save()
        self.assertTrue(self.son.is_bar_mitzvah)
        self.assertTrue(self.son.can_get_aliya)

        self.son.cannot_get_aliya = True
        self.son.save()
        self.assertFalse(self.son.can_get_aliya)

        self.son.cannot_get_aliya = False
        self.son.save()
        self.assertTrue(self.son.can_get_aliya)

        self.son.date_of_death = date.today()
        self.son.save()
        self.assertFalse(self.son.can_get_aliya)

    def test_marriage(self):
        self.assertFalse(self.son.is_married)
        self.assertIsNone(self.son.wife)
        self.assertFalse(self.wife.is_married_woman)

        self.son.wife = self.wife
        self.son.save()
        self.assertTrue(self.son.is_married)
        self.assertEquals(self.son.wife, self.wife)
        self.assertEquals(self.son.wife.husband, self.son)
        self.assertTrue(self.wife.is_married_woman)


class MaleMembersTestCase(TestCase):
    def setUp(self):
        self.synagogue = make_synagogue()
        self.father = Person.objects.create(formal_name='Dad', synagogue=self.synagogue,
                                            date_of_death=date(2018, 11, 11))
        self.mother = Person.objects.create(formal_name='Mom', synagogue=self.synagogue,
                                            date_of_death=date(2017, 3, 3))
        self.reuven = MaleMember.objects.create(
            formal_name='Reuven', synagogue=self.synagogue, last_name='Levi', date_of_birth=date(2000, 1, 1),
            father=self.father, mother=self.mother, yichus=Yichus.LEVI, bar_mitzvah_parasha=12,
            last_aliya_date=date(2019, 12, 1))
        self.wife = Member.objects.create(
            formal_name='Rivkah', synagogue=self.synagogue, last_name='Levi', date_of_birth=date(2000, 1, 1),
            father=Person.objects.create(formal_name='Father in Law', synagogue=self.synagogue),
            mother=Person.objects.create(formal_name='Mother in Law', synagogue=self.synagogue))
        self.shimon = MaleMember.objects.create(
            formal_name='Shimon', synagogue=self.synagogue, last_name='Levi', date_of_birth=date(2000, 1, 1),
            father=self.father, mother=self.mother, yichus=Yichus.LEVI, wife=self.wife)
        self.baby = Member.objects.create(
            formal_name='Shoshana', synagogue=self.synagogue, last_name='Levi', date_of_birth=date(2019, 1, 1),
            father=self.shimon, mother=self.wife)
        self.brother_in_law = MaleMember.objects.create(
            formal_name='Moshe', synagogue=self.synagogue, last_name='Cohen', date_of_birth=date(2000, 1, 1),
            father=self.wife.father, mother=self.wife.mother, yichus=Yichus.COHEN, last_aliya_date=date(2019, 11, 1))


class TestMaleMembersManager(MaleMembersTestCase):
    def test_cohanim(self):
        self.assertEquals(set(MaleMember.cohanim.all()), {self.brother_in_law})

    def test_leviim(self):
        self.assertEquals(set(MaleMember.leviim.all()), {self.reuven, self.shimon})


class TestAliyaPrecedence(MaleMembersTestCase):
    def test_bar_mitzvah_parasha_shabbat(self):
        self.assertFalse(self.reuven.is_bar_mitzvah_parasha_shabbat(HebrewDate(5780, 9, 1)))
        self.assertTrue(self.reuven.is_bar_mitzvah_parasha_shabbat(HebrewDate(5780, 10, 16)))
        self.assertTrue(self.reuven.is_bar_mitzvah_parasha_shabbat(HebrewDate(5780, 10, 21)))
        self.assertFalse(self.reuven.is_bar_mitzvah_parasha_shabbat(HebrewDate(5780, 10, 22)))
        self.assertEquals(self.reuven.next_bar_mitzvah_parasha_shabbat(HebrewDate(5780, 9, 1)),
                          HebrewDate(5780, 10, 21))
        self.assertEquals(self.reuven.next_bar_mitzvah_parasha_shabbat(HebrewDate(5780, 10, 21)),
                          HebrewDate(5780, 10, 21))
        self.assertEquals(self.reuven.next_bar_mitzvah_parasha_shabbat(HebrewDate(5780, 10, 22)),
                          HebrewDate(5781, 10, 25))

        # has no bar mitzvah parasha defined
        self.assertFalse(self.shimon.is_bar_mitzvah_parasha_shabbat())
        self.assertIsNone(self.shimon.next_bar_mitzvah_parasha_shabbat())

    def test_immediate_family_members(self):
        self.assertEquals(self.father.immediate_family_members, {self.reuven.member, self.shimon.member})
        self.assertEquals(self.mother.immediate_family_members, {self.reuven.member, self.shimon.member})
        self.assertEquals(self.reuven.immediate_family_members, {self.mother, self.father, self.shimon.member})
        self.assertEquals(self.shimon.immediate_family_members,
                          {self.mother, self.father, self.reuven.member, self.wife, self.baby})
        self.assertEquals(self.shimon.immediate_family_members,
                          {self.mother, self.father, self.reuven.member, self.wife, self.baby})
        self.assertEquals(self.wife.immediate_family_members,
                          {self.wife.mother, self.wife.father, self.shimon.member, self.brother_in_law.member,
                           self.baby})
        self.assertEquals(self.brother_in_law.immediate_family_members,
                          {self.wife.mother, self.wife.father, self.wife})

    def test_yahrzeit_shabbat(self):
        self.assertEquals(next_anniversary_of(self.reuven.father.hebrew_date_of_death, HebrewDate(5780, 8, 1)),
                          HebrewDate(5780, 9, 3))
        self.assertFalse(self.reuven.is_yahrzeit_shabbat(HebrewDate(5780, 8, 1)))
        self.assertTrue(self.reuven.is_yahrzeit_shabbat(HebrewDate(5780, 8, 28)))
        self.assertTrue(self.reuven.is_yahrzeit_shabbat(HebrewDate(5780, 9, 2)))
        self.assertFalse(self.reuven.is_yahrzeit_shabbat(HebrewDate(5780, 9, 3)))
        self.assertFalse(self.reuven.is_yahrzeit_shabbat(HebrewDate(5780, 9, 9)))
        self.assertEquals(self.reuven.next_yahrzeit_shabbatot(HebrewDate(5780, 8, 1)),
                          [HebrewDate(5780, 9, 2), HebrewDate(5780, 12, 4)])
        self.assertEquals(self.reuven.next_yahrzeit_shabbatot(HebrewDate(5780, 9, 1)),
                          [HebrewDate(5780, 9, 2), HebrewDate(5780, 12, 4)])
        self.assertEquals(self.reuven.next_yahrzeit_shabbatot(HebrewDate(5780, 9, 2)),
                          [HebrewDate(5780, 9, 2), HebrewDate(5780, 12, 4)])
        self.assertEquals(self.reuven.next_yahrzeit_shabbatot(HebrewDate(5780, 9, 3)),
                          [HebrewDate(5780, 12, 4), HebrewDate(5781, 8, 27)])

        # has no yahrzeits defined
        self.assertFalse(self.brother_in_law.is_yahrzeit_shabbat())
        self.assertEquals(self.brother_in_law.next_yahrzeit_shabbatot(), [])

    def test_aliya_precedence(self):
        self.assertEquals(self.reuven.get_aliya_precedence(HebrewDate(5780, 10, 21)),
                          AliyaPrecedenceReason.BAR_MITZVAH_PARASHA)
        self.assertEquals(self.shimon.get_aliya_precedence(HebrewDate(5780, 10, 21)),
                          AliyaPrecedenceReason.TIME_SINCE_LAST_ALIYA)
        self.assertEquals(self.shimon.get_aliya_precedence(HebrewDate(5780, 9, 2)), AliyaPrecedenceReason.YAHRZEIT)
        self.assertEquals(self.shimon.get_aliya_precedence(HebrewDate(5780, 9, 2)), AliyaPrecedenceReason.YAHRZEIT)
        self.assertIsNone(self.brother_in_law.get_aliya_precedence(HebrewDate(5780, 9, 2)))

    def test_suggested_olim(self):
        self.assertEquals(MaleMember.objects.get_suggested_olim(HebrewDate(5780, 10, 21)),
                          [(self.reuven, AliyaPrecedenceReason.BAR_MITZVAH_PARASHA),
                           (self.shimon, AliyaPrecedenceReason.TIME_SINCE_LAST_ALIYA)])
        self.assertEquals(MaleMember.objects.get_suggested_olim(HebrewDate(5780, 9, 2)),
                          [(self.shimon, AliyaPrecedenceReason.YAHRZEIT),
                           (self.reuven, AliyaPrecedenceReason.YAHRZEIT)])
        self.assertEquals(MaleMember.objects.get_suggested_olim(HebrewDate(5780, 11, 15)),
                          [(self.shimon, AliyaPrecedenceReason.TIME_SINCE_LAST_ALIYA),
                           (self.brother_in_law, AliyaPrecedenceReason.TIME_SINCE_LAST_ALIYA)])

        self.assertEquals(MaleMember.cohanim.get_suggested_olim(HebrewDate(5780, 11, 15)),
                          [(self.brother_in_law, AliyaPrecedenceReason.TIME_SINCE_LAST_ALIYA)])
        self.assertEquals(MaleMember.leviim.get_suggested_olim(HebrewDate(5780, 11, 15)),
                          [(self.shimon, AliyaPrecedenceReason.TIME_SINCE_LAST_ALIYA)])
