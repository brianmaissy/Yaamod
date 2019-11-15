from datetime import timedelta, date
from typing import Tuple, Set, List

from django.contrib.auth.models import Group, User
from django.db import models
from django_enumfield import enum
from pyluach.dates import HebrewDate
from pyluach.parshios import PARSHIOS, getparsha

from .lib.date_utils import nth_anniversary_of, to_hebrew_date, next_anniversary_of, next_reading_of_parasha


class Yichus(enum.Enum):
    COHEN = 1
    LEVI = 2
    ISRAEL = 3


class AliyaPrecedenceReason(enum.Enum):
    # in order of precedence
    YAHRZEIT = 1
    BAR_MITZVAH_PARASHA = 2
    TIME_SINCE_LAST_ALIYA = 3


class Synagogue(models.Model):
    name = models.TextField()
    admins = models.ForeignKey(Group, on_delete=models.CASCADE)
    member_creator = models.ForeignKey(User, on_delete=models.CASCADE)

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
        return to_hebrew_date(self.date_of_death, self.date_of_death_after_sunset)

    @property
    def children(self):
        return self.children_of_father.all() | self.children_of_mother.all()

    @property
    def immediate_family_members(self) -> Set['Member']:
        return set(self.children.all())

    def __str__(self):
        return self.formal_name


class Member(Person):
    manual_first_name = models.TextField(blank=True)
    last_name = models.TextField()
    date_of_birth = models.DateField()
    date_of_birth_after_sunset = models.BooleanField(default=False)
    father = models.ForeignKey(Person, on_delete=models.PROTECT, related_name='children_of_father')
    mother = models.ForeignKey(Person, on_delete=models.PROTECT, related_name='children_of_mother')

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
        return '{} {} {}'.format(self.formal_name, self.son_or_daughter, self.father.formal_name)

    @property
    def maternal_formal_name(self):
        return '{} {} {}'.format(self.formal_name, self.son_or_daughter, self.mother.formal_name)

    @property
    def hebrew_date_of_birth(self):
        return to_hebrew_date(self.date_of_birth, self.date_of_birth_after_sunset)

    def __str__(self):
        return self.full_name

    @property
    def is_male(self):
        return hasattr(self, 'male_member')

    @property
    def is_married_woman(self):
        return hasattr(self, 'husband')

    @property
    def immediate_family_members(self):
        family_members = super().immediate_family_members
        family_members.update((self.father, self.mother), self.father.children.all(), self.mother.children.all())
        if self.is_married_woman:
            family_members.add(self.husband.member)
        family_members.discard(self.member)
        return family_members


class MaleMemberManager(models.Manager):
    def get_suggested_olim(self, reference_date=None) -> List['MaleMember']:
        suggested_olim: Tuple[MaleMember, AliyaPrecedenceReason] = []
        for male_member in self.get_queryset().all():
            if male_member.can_get_aliya:
                precedence = male_member.get_aliya_precedence(reference_date)
                if precedence:
                    suggested_olim.append((male_member, precedence))
        return sorted(suggested_olim, key=lambda suggestion: (suggestion[1], suggestion[0].last_aliya_date or date.min))


class CohanimManager(MaleMemberManager):
    def get_queryset(self):
        return super().get_queryset().filter(yichus=Yichus.COHEN)


class LeviimManager(MaleMemberManager):
    def get_queryset(self):
        return super().get_queryset().filter(yichus=Yichus.LEVI)


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

    objects = MaleMemberManager()
    cohanim = CohanimManager()
    leviim = LeviimManager()

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

    def is_bar_mitzvah_parasha_shabbat(self, reference_date=None):
        if self.bar_mitzvah_parasha is None:
            return None
        if reference_date is None:
            reference_date = HebrewDate.today()
        parshiot = getparsha(reference_date.shabbos(), israel=True)
        return parshiot is not None and self.bar_mitzvah_parasha in parshiot

    def next_bar_mitzvah_parasha_shabbat(self, reference_date=None):
        if self.bar_mitzvah_parasha is None:
            return None
        else:
            return next_reading_of_parasha(self.bar_mitzvah_parasha, reference_date)

    @property
    def immediate_family_members(self):
        family_members = super().immediate_family_members
        if self.is_married:
            family_members.add(self.wife)
        return family_members

    def is_yahrzeit_shabbat(self, reference_date=None):
        if reference_date is None:
            reference_date = HebrewDate.today()
        upcoming_shabbat = reference_date.shabbos()
        for family_member in self.immediate_family_members:
            if family_member.is_deceased:  # chas v'shalom
                yahrzeit = next_anniversary_of(family_member.hebrew_date_of_death, reference_date)
                if upcoming_shabbat <= yahrzeit < upcoming_shabbat + 7:
                    return True

        return False

    def next_yahrzeit_shabbatot(self, reference_date=None):
        if reference_date is None:
            reference_date = HebrewDate.today()
        yahrzeit_shabbatot = set()
        for family_member in self.immediate_family_members:
            if family_member.is_deceased:  # chas v'shalom
                yahrzeit = next_anniversary_of(family_member.hebrew_date_of_death, reference_date)
                if yahrzeit.weekday() == 7:
                    # bo b'yom
                    yahrzeit_shabbatot.add(yahrzeit)
                else:
                    # the custom is to get an aliya the shabbat preceding the yahrzeit
                    yahrzeit_shabbat = yahrzeit.shabbos() - 7
                    if yahrzeit_shabbat >= reference_date:
                        yahrzeit_shabbatot.add(yahrzeit_shabbat)
                    else:
                        # we just passed the yahrzeit shabbat, but the yahrzeit itself is this week
                        # use next year's yahrzeit shabbat
                        next_yahrzeit = next_anniversary_of(family_member.hebrew_date_of_death, yahrzeit + 1)
                        if next_yahrzeit.weekday() == 7:
                            yahrzeit_shabbatot.add(next_yahrzeit)
                        else:
                            yahrzeit_shabbatot.add(next_yahrzeit.shabbos() - 7)
        return sorted(yahrzeit_shabbatot)

    @property
    def is_bar_mitzvah(self):
        return HebrewDate.today() >= self.bar_mitzvah_date

    @property
    def can_get_aliya(self):
        return self.is_bar_mitzvah and not self.is_deceased and not self.cannot_get_aliya

    def get_aliya_precedence(self, reference_date=None):
        if reference_date is None:
            reference_date = HebrewDate.today()
        if self.is_yahrzeit_shabbat(reference_date):
            return AliyaPrecedenceReason.YAHRZEIT
        elif self.is_bar_mitzvah_parasha_shabbat(reference_date):
            return AliyaPrecedenceReason.BAR_MITZVAH_PARASHA
        elif self.last_aliya_date is None or reference_date.to_pydate() - self.last_aliya_date > timedelta(days=90):
            return AliyaPrecedenceReason.TIME_SINCE_LAST_ALIYA

    @property
    def is_married(self):
        return self.wife is not None
