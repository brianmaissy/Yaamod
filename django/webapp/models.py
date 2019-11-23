import math
from datetime import date
from typing import Tuple, Set, List, Dict, Optional

from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models.query import QuerySet
from django_enumfield import enum
from pyluach.dates import HebrewDate
from pyluach.parshios import PARSHIOS, getparsha

from .lib.date_utils import nth_anniversary_of, to_hebrew_date, next_anniversary_of, \
    make_torah_reading_occasions_table, TorahReadingOccasion


class Yichus(enum.Enum):
    COHEN = 1
    LEVI = 2
    ISRAEL = 3


class AliyaPrecedenceReason(enum.Enum):
    # in order of precedence
    YAHRZEIT = 1
    BIRTHDAY = 2
    BAR_MITZVAH_PARASHA = 3


class Synagogue(models.Model):
    name = models.TextField()
    admins = models.ForeignKey(Group, on_delete=models.CASCADE)
    member_creator = models.ForeignKey(User, on_delete=models.CASCADE)
    in_israel = models.BooleanField(default=True)
    in_jerusalem = models.BooleanField(default=False)

    def get_torah_reading_occasions_table(self, year: int) -> Dict[HebrewDate, TorahReadingOccasion]:
        return make_torah_reading_occasions_table(year, self.in_israel, self.in_jerusalem)

    def get_olim(self, on_date: HebrewDate) -> List[Tuple['MaleMember', AliyaPrecedenceReason]]:
        suggested_olim: List[Tuple[MaleMember, AliyaPrecedenceReason]] = []
        for male_member in self.male_member_set.all():
            if male_member.can_get_aliya:
                suggested_olim.append((male_member, male_member.get_aliya_precedence(on_date)))
        return sorted(suggested_olim, key=lambda suggestion: (suggestion[1] or math.inf,
                                                              suggestion[0].last_aliya_date or date.min))

    @property
    def member_set(self) -> QuerySet:
        return Member.objects.filter(synagogue=self)

    @property
    def male_member_set(self) -> QuerySet:
        return MaleMember.objects.filter(synagogue=self)

    def __str__(self) -> str:
        return self.name


class Person(models.Model):
    synagogue = models.ForeignKey(Synagogue, on_delete=models.CASCADE)
    formal_name = models.TextField()
    date_of_death = models.DateField(null=True, blank=True)
    date_of_death_after_sunset = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'people'

    @property
    def is_deceased(self) -> bool:
        return self.date_of_death is not None

    @property
    def hebrew_date_of_death(self) -> HebrewDate:
        return to_hebrew_date(self.date_of_death, self.date_of_death_after_sunset)

    @property
    def children(self) -> QuerySet:
        return self.children_of_father.all() | self.children_of_mother.all()

    @property
    def immediate_family_members(self) -> Set['Member']:
        return set(self.children.all())

    def __str__(self) -> str:
        return self.formal_name


class Member(Person):
    manual_first_name = models.TextField(blank=True)
    last_name = models.TextField()
    date_of_birth = models.DateField()
    date_of_birth_after_sunset = models.BooleanField(default=False)
    father = models.ForeignKey(Person, on_delete=models.PROTECT, related_name='children_of_father')
    mother = models.ForeignKey(Person, on_delete=models.PROTECT, related_name='children_of_mother')

    @property
    def first_name(self) -> str:
        return self.manual_first_name or self.formal_name

    @property
    def full_name(self) -> str:
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def son_or_daughter(self) -> str:
        return 'בן' if self.is_male else 'בת'

    @property
    def paternal_formal_name(self) -> str:
        return '{} {} {}'.format(self.formal_name, self.son_or_daughter, self.father.formal_name)

    @property
    def maternal_formal_name(self) -> str:
        return '{} {} {}'.format(self.formal_name, self.son_or_daughter, self.mother.formal_name)

    @property
    def hebrew_date_of_birth(self) -> HebrewDate:
        return to_hebrew_date(self.date_of_birth, self.date_of_birth_after_sunset)

    def __str__(self) -> str:
        return self.full_name

    @property
    def is_male(self) -> bool:
        return hasattr(self, 'male_member')

    @property
    def is_married_woman(self) -> bool:
        return hasattr(self, 'husband')

    @property
    def immediate_family_members(self) -> Set['Member']:
        family_members = super().immediate_family_members
        family_members.update((self.father, self.mother), self.father.children.all(), self.mother.children.all())
        if self.is_married_woman:
            family_members.add(self.husband.member)
        family_members.discard(self.member)
        return family_members


class MaleMember(Member):
    yichus = enum.EnumField(Yichus, default=Yichus.ISRAEL)
    cannot_get_aliya = models.BooleanField(default=False)
    can_be_hazan = models.BooleanField(default=False)
    can_read_torah = models.BooleanField(default=False)
    can_read_haftarah = models.BooleanField(default=False)
    bar_mitzvah_parasha = models.IntegerField(null=True, blank=True, choices=enumerate(PARSHIOS))
    last_aliya_date = models.DateField(null=True, blank=True)
    wife = models.OneToOneField(Member, on_delete=models.CASCADE, null=True, blank=True, related_name='husband')
    # this is necessary because of a bug in Django.
    # see https://code.djangoproject.com/ticket/29998
    member_ptr = models.OneToOneField(Member, on_delete=models.CASCADE, parent_link=True, related_name='male_member')

    @property
    def yichus_name(self) -> 'str':
        return Yichus.label(self.yichus).capitalize()

    @property
    def bar_mitzvah_parasha_name(self) -> Optional[str]:
        if self.bar_mitzvah_parasha is None:
            return None
        else:
            return PARSHIOS[self.bar_mitzvah_parasha]

    @property
    def bar_mitzvah_date(self) -> HebrewDate:
        return nth_anniversary_of(self.hebrew_date_of_birth, 13)

    def is_bar_mitzvah_parasha_shabbat(self, on_date: HebrewDate) -> bool:
        if self.bar_mitzvah_parasha is None:
            return False
        if on_date.weekday() != 7:
            return False
        parshiot = getparsha(on_date, israel=True)
        return parshiot is not None and self.bar_mitzvah_parasha in parshiot

    @property
    def immediate_family_members(self) -> Set[Member]:
        family_members = super().immediate_family_members
        if self.is_married:
            family_members.add(self.wife)
        return family_members

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

    @property
    def is_bar_mitzvah(self) -> bool:
        return HebrewDate.today() >= self.bar_mitzvah_date

    @property
    def can_get_aliya(self) -> bool:
        return self.is_bar_mitzvah and not self.is_deceased and not self.cannot_get_aliya

    def get_aliya_precedence(self, on_date: HebrewDate) -> Optional[int]:
        if not self.can_get_aliya:
            return None

        if self.needs_yahrzeit_aliya(on_date):
            return AliyaPrecedenceReason.YAHRZEIT
        elif self.needs_birthday_aliya(on_date):
            return AliyaPrecedenceReason.BIRTHDAY
        elif self.is_bar_mitzvah_parasha_shabbat(on_date):
            return AliyaPrecedenceReason.BAR_MITZVAH_PARASHA
        else:
            return None

    @property
    def is_married(self) -> bool:
        return self.wife is not None
