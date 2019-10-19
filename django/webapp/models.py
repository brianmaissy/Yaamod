from django.db import models
from django.contrib.auth.models import Group
from django.core.exceptions import SuspiciousOperation
from django_enumfield import enum
from pyluach.dates import HebrewDate

from .lib.date_utils import nth_anniversary_of


class Yichus(enum.Enum):
    COHEN = 1
    LEVI = 2
    ISRAEL = 3


class Synagogue(models.Model):
    name = models.TextField()
    admins = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class Person(models.Model):
    synagogue = models.ForeignKey(Synagogue, on_delete=models.CASCADE)
    formal_name = models.TextField()
    date_of_death = models.DateField(null=True, blank=True)
    date_of_death_after_sunset = models.BooleanField(default=False)

    @property
    def children(self):
        return self.children_of_father.all() | self.children_of_mother.all()

    def __str__(self):
        return self.formal_name


class Member(Person):
    manual_first_name = models.TextField(blank=True)
    last_name = models.TextField()
    date_of_birth = models.DateField()
    date_of_birth_after_sunset = models.BooleanField(default=False)
    father = models.ForeignKey(Person, on_delete=models.PROTECT,
                               related_name='children_of_father')
    mother = models.ForeignKey(Person, on_delete=models.PROTECT,
                               related_name='children_of_mother')

    @property
    def first_name(self):
        return self.manual_first_name or self.formal_name

    @property
    def full_name(self):
        return ' '.join(name for name in (self.first_name, self.last_name))

    @property
    def hebrew_date_of_birth(self):
        hebrew_date = HebrewDate.from_pydate(self.date_of_birth)
        if self.date_of_birth_after_sunset:
            hebrew_date += 1
        return hebrew_date

    def __str__(self):
        return self.full_name

    @property
    def bar_mitzvah_date(self):
        return nth_anniversary_of(self.hebrew_date_of_birth, 13)

    @property
    def is_bar_mitzvah(self):
        return HebrewDate.today() >= self.bar_mitzvah_date

    @property
    def is_male(self):
        return hasattr(self, 'malemember')


class MaleMember(Member):
    yichus = enum.EnumField(Yichus, default=Yichus.ISRAEL)
    cannot_get_aliya = models.BooleanField(default=False)
    can_be_hazan = models.BooleanField(default=False)
    can_read_torah = models.BooleanField(default=False)
    can_read_haftarah = models.BooleanField(default=False)
    parashat_bar_mitzvah = models.IntegerField(null=True, blank=True)
    last_aliya_date = models.DateField(null=True, blank=True)
    wife = models.OneToOneField(Member, on_delete=models.CASCADE,
                                null=True, blank=True,
                                related_name='husband')
    # this is necessary because of a bug in Django.
    # see https://code.djangoproject.com/ticket/29998
    member_ptr = models.OneToOneField(Member, on_delete=models.CASCADE,
                                      parent_link=True)

    @property
    def is_married(self):
        return self.wife is not None


def get_from_model(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        raise SuspiciousOperation()
