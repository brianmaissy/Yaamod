from django.contrib.auth.models import Group
from django.core.exceptions import SuspiciousOperation
from django.db import models
from django_enumfield import enum
from pyluach.dates import HebrewDate
from pyluach.parshios import PARSHIOS

from .lib.date_utils import nth_anniversary_of, to_hebrew_date


class Yichus(enum.Enum):
    COHEN = 1
    LEVI = 2
    ISRAEL = 3


class Synagogue(models.Model):
    name = models.TextField()
    admins = models.ForeignKey(Group, on_delete=models.CASCADE)

    @property
    def member_set(self):
        return Member.objects.filter(synagogue=self)

    def __str__(self):
        return self.name


class Person(models.Model):
    synagogue = models.ForeignKey(Synagogue, on_delete=models.CASCADE)
    formal_name = models.TextField()
    date_of_death = models.DateField(null=True, blank=True)
    date_of_death_after_sunset = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'people'

    @property
    def is_deceased(self):
        return self.date_of_death is not None

    @property
    def hebrew_date_of_death(self):
        return to_hebrew_date(self.date_of_death,
                              self.date_of_death_after_sunset)

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
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def son_or_daughter(self):
        return 'בן' if self.is_male else 'בת'

    @property
    def paternal_formal_name(self):
        return '{} {} {}'.format(self.formal_name, self.son_or_daughter,
                                 self.father.formal_name)

    @property
    def maternal_formal_name(self):
        return '{} {} {}'.format(self.formal_name, self.son_or_daughter,
                                 self.mother.formal_name)

    @property
    def hebrew_date_of_birth(self):
        return to_hebrew_date(self.date_of_birth,
                              self.date_of_birth_after_sunset)

    def __str__(self):
        return self.full_name

    @property
    def is_male(self):
        return hasattr(self, 'male_member')

    @property
    def is_married_woman(self):
        return hasattr(self, 'husband')


class MaleMember(Member):
    yichus = enum.EnumField(Yichus, default=Yichus.ISRAEL)
    cannot_get_aliya = models.BooleanField(default=False)
    can_be_hazan = models.BooleanField(default=False)
    can_read_torah = models.BooleanField(default=False)
    can_read_haftarah = models.BooleanField(default=False)
    bar_mitzvah_parasha = models.IntegerField(null=True, blank=True,
                                              choices=enumerate(PARSHIOS))
    last_aliya_date = models.DateField(null=True, blank=True)
    wife = models.OneToOneField(Member, on_delete=models.CASCADE,
                                null=True, blank=True,
                                related_name='husband')
    # this is necessary because of a bug in Django.
    # see https://code.djangoproject.com/ticket/29998
    member_ptr = models.OneToOneField(Member, on_delete=models.CASCADE,
                                      parent_link=True,
                                      related_name='male_member')

    @property
    def yichus_name(self):
        return Yichus.label(self.yichus).capitalize()

    @property
    def bar_mitzvah_parasha_name(self):
        if self.bar_mitzvah_parasha is None:
            return None
        else:
            return PARSHIOS[self.bar_mitzvah_parasha]

    @property
    def bar_mitzvah_date(self):
        return nth_anniversary_of(self.hebrew_date_of_birth, 13)

    @property
    def is_bar_mitzvah(self):
        return HebrewDate.today() >= self.bar_mitzvah_date

    @property
    def can_get_aliya(self):
        return (self.is_bar_mitzvah and
                not self.is_deceased and
                not self.cannot_get_aliya)

    @property
    def is_married(self):
        return self.wife is not None


def get_from_model(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        raise SuspiciousOperation()
