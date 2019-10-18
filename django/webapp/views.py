from django.views.generic import DetailView, ListView, View
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import SuspiciousOperation

from webapp.models import Synagogue, Member

import abc


def get_from_dict(data, *names):
    args = []
    for name in names:
        arg = data.get(name)
        if arg is None:
            raise SuspiciousOperation()
        args.append(arg)
    if len(args) == 1:
        args = args[0]
    return args


class SynagoguePermChecker(UserPassesTestMixin):
    """
    an abstract class to check if the user has admin permissions for the requested synagogue.
    every child class need to implement get_synagogue which get the synagogue we are trying to query about
    from the request. It will return 403 if he is unauthorized.
    This class should be the first to inherit from.
    """
    raise_exception = True

    def test_func(self):
        synagogue = self.get_synagogue()
        return synagogue.admins in self.request.user.groups.all()

    @abc.abstractmethod
    def get_synagogue(self):
        pass


class SynagogueList(ListView):
    model = Synagogue


class SynagogueDetail(SynagoguePermChecker, DetailView):
    model = Synagogue

    def get_synagogue(self):
        pk = get_from_dict(self.kwargs, 'pk')
        return Synagogue.objects.get(pk=pk)


class MemberDetail(SynagoguePermChecker, DetailView):
    model = Member

    def get_synagogue(self):
        member_pk = get_from_dict(self.kwargs, 'pk')
        member = Member.objects.get(pk=member_pk)
        return member.synagogue


class LoginView(View):
    def post(self, request):
        username, password = get_from_dict(request.POST, 'username', 'password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponse()
        else:
            return HttpResponseForbidden()


class LogoutView(View):
    def post(self, request):
        logout(request)
        return HttpResponse()


class AddUserView(SynagoguePermChecker, View):
    def post(self, request):
        username, password, pk = get_from_dict(request.POST, 'username', 'password', 'pk')

        user = User.objects.create_user(username)
        user.set_password(password)

        synagogue = Synagogue.objects.get(pk=pk)
        synagogue.admins.add(user)

        user.save()
        return HttpResponse()

    def get_synagogue(self):
        pk = get_from_dict(self.request.POST, 'pk')
        return Synagogue.objects.get(pk=pk)


class AddSynagogueView(View):
    def post(self, request):
        name, username, password = get_from_dict(request.POST, 'name', 'username', 'password')
        admins = Group.objects.create(name=u'synagogue_{0}_admins'.format(name))
        Synagogue.objects.create(name=name, admins=admins)
        user = User.objects.create_user(username, password=password)
        user.groups.add(admins)
        user.save()
        return HttpResponse()
