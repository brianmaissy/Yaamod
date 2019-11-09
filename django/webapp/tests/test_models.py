from datetime import date

from django.contrib.auth.models import Group, User
from django.test import TestCase
from pyluach.dates import HebrewDate

from webapp.lib.date_utils import nth_anniversary_of
from webapp.models import Synagogue, Person, Member, MaleMember, Yichus


class MembersTestCase(TestCase):
    def setUp(self):
        today = date.today()
        admins = Group.objects.create(name='admins')
        self.synagogue = Synagogue.objects.create(
            name='Klal Yisrael', admins=admins, member_creator=User.objects.create(username='admin'))
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
