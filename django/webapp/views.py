from django.views.generic import DetailView, ListView

from webapp.models import Synagogue, Member


class SynagogueList(ListView):
    model = Synagogue


class SynagogueDetail(DetailView):
    model = Synagogue


class MemberDetail(DetailView):
    model = Member
