from datetime import date

from django.contrib.auth.models import Group
from django.test import TestCase
from pyluach.dates import HebrewDate

from webapp.lib.date_utils import nth_anniversary_of
from webapp.models import Synagogue, Person, Member, MaleMember, Yichus


class TestSynagogue(TestCase):
    def test_members(self):
        synagogue = Synagogue.objects.create(
            name='Klal Yisrael', admins=Group.objects.create(name='admins'))
        father = Person.objects.create(formal_name='Dad', synagogue=synagogue)
        mother = Person.objects.create(formal_name='Mom', synagogue=synagogue)
        daughter = Member.objects.create(formal_name='Sarah',
                                         synagogue=synagogue, last_name='Levi',
                                         date_of_birth=date(2019, 1, 1),
                                         father=father, mother=mother)
        self.assertEquals(synagogue.person_set.count(), 3)
        self.assertEquals(synagogue.member_set.count(), 1)
        self.assertEquals(synagogue.member_set.get(), daughter)
        self.assertIsInstance(synagogue.member_set.get(), Member)


class TestPerson(TestCase):
    def test_sanity(self):
        synagogue = Synagogue.objects.create(
            name='Klal Yisrael', admins=Group.objects.create(name='admins'))
        person = Person.objects.create(formal_name='Reuven',
                                       synagogue=synagogue)
        self.assertEquals(str(person), 'Reuven')
        self.assertIsNone(person.hebrew_date_of_death)
        self.assertFalse(person.children.exists())

        person.date_of_death = date(2019, 1, 1)
        person.save()
        self.assertEquals(person.hebrew_date_of_death,
                          HebrewDate(5779, 10, 24))

    def test_children(self):
        synagogue = Synagogue.objects.create(
            name='Klal Yisrael', admins=Group.objects.create(name='admins'))
        father = Person.objects.create(formal_name='Dad', synagogue=synagogue)
        mother = Person.objects.create(formal_name='Mom', synagogue=synagogue)
        daughter = Member.objects.create(formal_name='Sarah',
                                         synagogue=synagogue, last_name='Levi',
                                         date_of_birth=date(2019, 1, 1),
                                         father=father, mother=mother)
        self.assertEquals(list(father.children.all()), [daughter])
        self.assertEquals(list(father.children_of_father.all()), [daughter])
        self.assertEquals(list(father.children_of_mother.all()), [])
        self.assertEquals(list(mother.children.all()), [daughter])
        self.assertEquals(list(mother.children_of_father.all()), [])
        self.assertEquals(list(mother.children_of_mother.all()), [daughter])


class TestMember(TestCase):
    def test_sanity(self):
        synagogue = Synagogue.objects.create(
            name='Klal Yisrael', admins=Group.objects.create(name='admins'))
        father = Person.objects.create(formal_name='Dad', synagogue=synagogue)
        mother = Person.objects.create(formal_name='Mom', synagogue=synagogue)
        daughter = Member.objects.create(formal_name='Sarah',
                                         synagogue=synagogue, last_name='Levi',
                                         date_of_birth=date(2019, 1, 1),
                                         father=father, mother=mother)
        self.assertEquals(daughter.first_name, 'Sarah')
        self.assertEquals(daughter.full_name,  'Sarah Levi')
        self.assertEquals(str(daughter),  'Sarah Levi')
        daughter.manual_first_name = 'Sarai'
        daughter.save()
        self.assertEquals(daughter.first_name, 'Sarai')
        self.assertEquals(daughter.full_name,  'Sarai Levi')
        self.assertEquals(str(daughter),  'Sarai Levi')

        self.assertFalse(daughter.is_male)
        self.assertEquals(daughter.hebrew_date_of_birth,
                          HebrewDate(5779, 10, 24))

        self.assertIn(daughter, daughter.father.children.all())
        self.assertIn(daughter, daughter.mother.children.all())

    def test_full_formal_names(self):
        synagogue = Synagogue.objects.create(
            name='Klal Yisrael', admins=Group.objects.create(name='admins'))
        father = Person.objects.create(formal_name='Dad', synagogue=synagogue)
        mother = Person.objects.create(formal_name='Mom', synagogue=synagogue)
        son = MaleMember.objects.create(formal_name='Reuven',
                                        synagogue=synagogue, last_name='Levi',
                                        date_of_birth=date.today(),
                                        father=father, mother=mother,
                                        yichus=Yichus.LEVI)
        daughter = Member.objects.create(formal_name='Sarah',
                                         synagogue=synagogue, last_name='Levi',
                                         date_of_birth=date.today(),
                                         father=father, mother=mother)
        self.assertEquals(son.paternal_formal_name, 'Reuven בן Dad')
        self.assertEquals(son.maternal_formal_name, 'Reuven בן Mom')
        self.assertEquals(daughter.paternal_formal_name, 'Sarah בת Dad')
        self.assertEquals(daughter.maternal_formal_name, 'Sarah בת Mom')


class TestMaleMember(TestCase):
    def test_sanity(self):
        synagogue = Synagogue.objects.create(
            name='Klal Yisrael', admins=Group.objects.create(name='admins'))
        father = Person.objects.create(formal_name='Dad', synagogue=synagogue)
        mother = Person.objects.create(formal_name='Mom', synagogue=synagogue)
        son = MaleMember.objects.create(formal_name='Reuven',
                                        synagogue=synagogue, last_name='Levi',
                                        date_of_birth=date.today(),
                                        father=father, mother=mother,
                                        yichus=Yichus.LEVI)

        self.assertEquals(son.yichus, Yichus.LEVI)
        self.assertEquals(son.yichus_name, 'Levi')

        self.assertIsNone(son.bar_mitzvah_parasha)
        self.assertIsNone(son.bar_mitzvah_parasha_name)
        son.bar_mitzvah_parasha = 0
        self.assertEquals(son.bar_mitzvah_parasha_name, 'Beraishis')

        self.assertIsInstance(son.member_ptr, Member)
        son_as_member = Member.objects.get(id=son.id)
        self.assertIsInstance(son_as_member, Member)
        self.assertIsInstance(son_as_member.male_member, MaleMember)

    def test_can_get_aliya(self):
        synagogue = Synagogue.objects.create(
            name='Klal Yisrael', admins=Group.objects.create(name='admins'))
        father = Person.objects.create(formal_name='Dad', synagogue=synagogue)
        mother = Person.objects.create(formal_name='Mom', synagogue=synagogue)
        son = MaleMember.objects.create(formal_name='Reuven',
                                        synagogue=synagogue, last_name='Levi',
                                        date_of_birth=date.today(),
                                        father=father, mother=mother,
                                        yichus=Yichus.LEVI)
        self.assertEquals(son.bar_mitzvah_date,
                          nth_anniversary_of(son.hebrew_date_of_birth, 13))
        self.assertFalse(son.is_bar_mitzvah)
        self.assertFalse(son.can_get_aliya)

        son.date_of_birth = son.date_of_birth.replace(
            year=son.date_of_birth.year - 14)
        son.save()
        self.assertTrue(son.is_bar_mitzvah)
        self.assertTrue(son.can_get_aliya)

        son.cannot_get_aliya = True
        son.save()
        self.assertFalse(son.can_get_aliya)

        son.cannot_get_aliya = False
        son.save()
        self.assertTrue(son.can_get_aliya)

        son.date_of_death = date.today()
        son.save()
        self.assertFalse(son.can_get_aliya)

    def test_marriage(self):
        synagogue = Synagogue.objects.create(
            name='Klal Yisrael', admins=Group.objects.create(name='admins'))
        father = Person.objects.create(formal_name='Dad', synagogue=synagogue)
        mother = Person.objects.create(formal_name='Mom', synagogue=synagogue)
        wife = Member.objects.create(formal_name='Rivkah', synagogue=synagogue,
                                     last_name='Shtern',
                                     date_of_birth=date.today(),
                                     # yeah they're siblings, sorry, just
                                     # trying to save on the number of objects
                                     father=father, mother=mother)
        son = MaleMember.objects.create(formal_name='Reuven',
                                        synagogue=synagogue, last_name='Levi',
                                        date_of_birth=date.today(),
                                        father=father, mother=mother,
                                        yichus=Yichus.LEVI)
        self.assertFalse(son.is_married)
        self.assertIsNone(son.wife)
        self.assertFalse(wife.is_married_woman)

        son.wife = wife
        son.save()
        self.assertTrue(son.is_married)
        self.assertEquals(son.wife, wife)
        self.assertEquals(son.wife.husband, son)
        self.assertTrue(wife.is_married_woman)
