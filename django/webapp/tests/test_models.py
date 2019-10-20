from datetime import date

from django.test import TestCase
from pyluach.dates import HebrewDate

from webapp.lib.date_utils import nth_anniversary_of
from webapp.models import Synagogue, Person, Member, MaleMember, Yichus


class TestPerson(TestCase):
    def test_sanity(self):
        synagogue = Synagogue.objects.create(name='Klal Yisrael')
        person = Person.objects.create(formal_name='Reuven',
                                       synagogue=synagogue)
        self.assertEquals(str(person), 'Reuven')
        self.assertIsNone(person.hebrew_date_of_death)
        self.assertEquals(len(person.children.all()), 0)

        person.date_of_death = date(2019, 1, 1)
        person.save()
        self.assertEquals(person.hebrew_date_of_death,
                          HebrewDate(5779, 10, 24))

    def test_children(self):
        synagogue = Synagogue.objects.create(name='Klal Yisrael')
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
        synagogue = Synagogue.objects.create(name='Klal Yisrael')
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


class TestMaleMember(TestCase):
    def test_can_get_aliya(self):
        synagogue = Synagogue.objects.create(name='Klal Yisrael')
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

    def test_marriage(self):
        synagogue = Synagogue.objects.create(name='Klal Yisrael')
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

        son.wife = wife
        son.save()
        self.assertTrue(son.is_married)
        self.assertEquals(son.wife, wife)
        self.assertEquals(son.wife.husband, son)
