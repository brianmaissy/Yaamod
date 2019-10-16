from django.test import TestCase

from .models import Member


class MemberModelTests(TestCase):
    def test_full_name(self):
        member = Member(first_name='John', last_name='Doe')
        self.assertEquals(member.full_name, 'John Doe')

    def test_yichus(self):
        member = Member()
        self.assertEquals(member.yichus, 'Yisrael')
        member.is_levi = True
        self.assertEquals(member.yichus, 'Levi')
        member.is_cohen = True
        self.assertEquals(member.yichus, 'Cohen')
