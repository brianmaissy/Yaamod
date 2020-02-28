import math
from datetime import date

from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models.query import QuerySet
from django_enumfield import enum
from pyluach.dates import HebrewDate
from pyluach.parshios import PARSHIOS, getparsha
from typing import Tuple, Set, List, Dict, Optional

from .lib.date_utils import nth_anniversary_of, to_hebrew_date, next_anniversary_of, \
    make_torah_reading_occasions_table, TorahReadingOccasion


class Gender(enum.Enum):
    MALE = 1
    FEMALE = 2


class Yichus(enum.Enum):
    COHEN = 1
    LEVI = 2
    ISRAEL = 3


class AliyaPrecedenceReason(enum.Enum):
    # in order of precedence
    YAHRZEIT = 1
    BIRTHDAY = 2
    BAR_MITZVAH_PARASHA = 3


class CannotGetAliya(Exception):
    pass


class Synagogue(models.Model):
    name = models.TextField()
    member_creator = models.ForeignKey(User, on_delete=models.CASCADE)
    in_israel = models.BooleanField(default=True)
    in_jerusalem = models.BooleanField(default=False)

    def get_torah_reading_occasions_table(self, year: int) -> Dict[HebrewDate, TorahReadingOccasion]:
        return make_torah_reading_occasions_table(year, self.in_israel, self.in_jerusalem)

    def get_olim(self, on_date: HebrewDate) -> List[Tuple['Person', AliyaPrecedenceReason]]:
        suggested_olim: List[Tuple[Person, AliyaPrecedenceReason]] = []
        for male_member in self.male_members.all():
            if male_member.can_get_aliya:
                suggested_olim.append((male_member, male_member.get_aliya_precedence(on_date)))
        suggested_olim.sort(key=lambda suggestion: (suggestion[1] or math.inf,
                                                    suggestion[0].last_aliya_date or date.min))
        return suggested_olim

    @property
    def people(self) -> QuerySet:
        return Person.objects.filter(synagogue=self)

    @property
    def members(self) -> QuerySet:
        return self.people.filter(is_member=True)

    @property
    def male_members(self) -> QuerySet:
        return self.members.filter(gender=Gender.MALE)

    def __str__(self) -> str:
        return self.name


class Person(models.Model):
    synagogue = models.ForeignKey(Synagogue, on_delete=models.CASCADE)

    first_name = models.TextField()
    last_name = models.TextField(blank=True)
    maiden_name = models.TextField(blank=True)

    date_of_birth = models.DateField(null=True, blank=True)
    date_of_birth_after_sunset = models.BooleanField(default=False)
    date_of_death = models.DateField(null=True, blank=True)
    date_of_death_after_sunset = models.BooleanField(default=False)

    gender = enum.EnumField(Gender, null=True, blank=True, default=None)
    is_member = models.BooleanField(default=False)

    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    phone_number = models.TextField(blank=True)

    yichus = enum.EnumField(Yichus, null=True, blank=True, default=None)
    manual_paternal_name = models.TextField(blank=True)
    manual_maternal_name = models.TextField(blank=True)

    cannot_get_aliya = models.BooleanField(default=False)
    can_be_hazan = models.BooleanField(default=False)
    can_read_torah = models.BooleanField(default=False)
    can_read_haftarah = models.BooleanField(default=False)
    bar_mitzvah_parasha = models.IntegerField(null=True, blank=True, choices=enumerate(PARSHIOS))
    last_aliya_date = models.DateField(null=True, blank=True)

    father = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL,
                               related_name='children_of_father')
    mother = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL,
                               related_name='children_of_mother')
    wife = models.OneToOneField('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='husband')

    class Meta:
        verbose_name_plural = 'people'

    @property
    def full_name(self) -> str:
        full_name = self.first_name
        if self.last_name:
            full_name += ' ' + self.last_name
        return full_name

    def __str__(self) -> str:
        return self.full_name

    @property
    def hebrew_date_of_birth(self) -> Optional[HebrewDate]:
        return to_hebrew_date(self.date_of_birth, self.date_of_birth_after_sunset)

    @property
    def hebrew_date_of_death(self) -> Optional[HebrewDate]:
        return to_hebrew_date(self.date_of_death, self.date_of_death_after_sunset)

    @property
    def is_deceased(self) -> bool:
        return self.date_of_death is not None

    @property
    def yichus_name(self) -> Optional[str]:
        if self.yichus is None:
            return None
        else:
            return Yichus.label(self.yichus).capitalize()

    @property
    def son_or_daughter(self) -> Optional[str]:
        if self.gender == Gender.MALE:
            return 'בן'
        elif self.gender == Gender.FEMALE:
            return 'בת'
        else:
            return None

    @property
    def paternal_name(self) -> Optional[str]:
        if self.manual_paternal_name:
            return self.manual_paternal_name
        son_or_daughter = self.son_or_daughter
        if son_or_daughter is None or self.father is None:
            return None
        else:
            return '{} {} {}'.format(self.first_name, son_or_daughter, self.father.first_name)

    @property
    def maternal_name(self) -> Optional[str]:
        if self.manual_maternal_name:
            return self.manual_maternal_name
        son_or_daughter = self.son_or_daughter
        if son_or_daughter is None or self.mother is None:
            return None
        else:
            return '{} {} {}'.format(self.first_name, son_or_daughter, self.mother.first_name)

    @property
    def is_married_man(self) -> bool:
        return self.wife is not None

    @property
    def is_married_woman(self) -> bool:
        return hasattr(self, 'husband')

    @property
    def is_married(self) -> bool:
        return ((self.gender == Gender.MALE and self.is_married_man) or
                (self.gender == Gender.FEMALE and self.is_married_woman))

    @property
    def children(self) -> QuerySet:
        return self.children_of_father.all() | self.children_of_mother.all()

    @property
    def immediate_family_members(self) -> Set['Person']:
        family_members = set()
        # parents and siblings
        if self.father:
            family_members.add(self.father)
            family_members.update(self.father.children.all())
        if self.mother:
            family_members.add(self.mother)
            family_members.update(self.mother.children.all())
        # remove self (was added as a sibling)
        family_members.discard(self)
        # spouse
        if self.is_married_man:
            family_members.add(self.wife)
        if self.is_married_woman:
            family_members.add(self.husband)
        # children
        family_members.update(self.children.all())
        return family_members

    @property
    def bar_mitzvah_date(self) -> Optional[HebrewDate]:
        if self.gender == Gender.MALE and self.date_of_birth is not None:
            return nth_anniversary_of(self.hebrew_date_of_birth, 13)
        else:
            return None

    @property
    def is_bar_mitzvah(self) -> bool:
        bar_mitzvah_date = self.bar_mitzvah_date
        if bar_mitzvah_date is None:
            return False
        else:
            return HebrewDate.today() >= self.bar_mitzvah_date

    @property
    def can_get_aliya(self) -> bool:
        return self.is_bar_mitzvah and not self.is_deceased and not self.cannot_get_aliya

    @property
    def bar_mitzvah_parasha_name(self) -> Optional[str]:
        if self.bar_mitzvah_parasha is None:
            return None
        else:
            return PARSHIOS[self.bar_mitzvah_parasha]

    @property
    def last_aliya_hebrew_date(self) -> Optional[HebrewDate]:
        return to_hebrew_date(self.last_aliya_date, False)

    def is_bar_mitzvah_parasha_shabbat(self, on_date: HebrewDate) -> bool:
        if self.bar_mitzvah_parasha is None:
            return False
        if on_date.weekday() != 7:
            return False
        parshiot = getparsha(on_date, israel=True)
        return parshiot is not None and self.bar_mitzvah_parasha in parshiot

    def needs_yahrzeit_aliya(self, on_date: HebrewDate) -> bool:
        for family_member in self.immediate_family_members:
            if family_member.is_deceased:  # chas v'shalom
                yahrzeit = next_anniversary_of(family_member.hebrew_date_of_death, on_date)
                if yahrzeit == on_date:
                    # bo b'yom
                    return True
                elif on_date.weekday() == 7 and on_date < yahrzeit < on_date + 7:
                    # the custom is to get an aliya the shabbat preceding the yahrzeit
                    return True
        return False

    def needs_birthday_aliya(self, on_date: HebrewDate) -> bool:
        birthday = next_anniversary_of(self.hebrew_date_of_birth, on_date)
        if birthday == on_date:
            # bo b'yom
            return True
        elif on_date.weekday() == 7 and on_date < birthday < on_date + 7:
            # the custom is to get an aliya the shabbat preceding the birthday
            return True
        else:
            return False

    def get_aliya_precedence(self, on_date: HebrewDate) -> Optional[int]:
        if not self.can_get_aliya:
            raise CannotGetAliya()

        if self.needs_yahrzeit_aliya(on_date):
            return AliyaPrecedenceReason.YAHRZEIT
        elif self.needs_birthday_aliya(on_date):
            return AliyaPrecedenceReason.BIRTHDAY
        elif self.is_bar_mitzvah_parasha_shabbat(on_date):
            return AliyaPrecedenceReason.BAR_MITZVAH_PARASHA
        else:
            return None


class UserToSynagogue(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    synagogue = models.ForeignKey(Synagogue, on_delete=models.CASCADE)
