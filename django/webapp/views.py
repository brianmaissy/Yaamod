from django.views.generic import DetailView, ListView, View
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth.forms import PasswordResetForm

from webapp.models import Synagogue, Member, get_from_model
from webapp.forms import AddSynagogueForm, LoginForm, AddUserToSynagogueForm

import abc


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


class MyFormView(View):
    """
    django's FormView is not what we need since it does a lot that we don't need (e.g implement a GET that render
    template, but we only want a simple post). So this simple FormView is exactly what we need. it is separated to
    a lot of functions to let the children hook it. The usual child should just add
    form = <MyForm>
    and let the form do all the job.
    """
    form = NotImplementedError

    def post(self, request):
        form = self.get_form()
        self.save(form)
        return HttpResponse()

    def get_form(self):
        # we validate the form in get_form since the form is useless before it is validated
        form = self.form(self.request.POST)
        if not self.validate(form):
            raise SuspiciousOperation()
        return form

    def validate(self, form):
        return form.is_valid()

    def save(self, form, *args, **kwargs):
        form.save(*args, **kwargs)


class SafeGetMixin:
    def safe_get(self, *names):
        args = []
        for name in names:
            arg = self.kwargs.get(name)
            if arg is None:
                raise SuspiciousOperation()
            args.append(arg)
        if len(args) == 1:
            args = args[0]
        return args


class SynagoguePermCheckFormView(SynagoguePermChecker, MyFormView):
    def get_synagogue(self):
        form = self.get_form()
        return form.get_synagogue()


class SynagogueList(ListView):
    model = Synagogue


class SynagogueDetail(SynagoguePermChecker, DetailView, SafeGetMixin):
    model = Synagogue

    def get_synagogue(self):
        pk = self.safe_get('pk')
        return get_from_model(Synagogue, pk=pk)


class MemberDetail(SynagoguePermChecker, DetailView, SafeGetMixin):
    model = Member

    def get_synagogue(self):
        member_pk = self.safe_get('pk')
        member = get_from_model(Member, pk=member_pk)
        return member.synagogue


class LoginView(MyFormView):
    form = LoginForm

    def save(self, form, *args, **kwargs):
        kwargs['request'] = self.request
        super().save(form, *args, **kwargs)


class LogoutView(View):
    def post(self, request):
        logout(request)
        return HttpResponse()


class AddUserView(SynagoguePermCheckFormView):
    form = AddUserToSynagogueForm


class AddSynagogueView(MyFormView):
    form = AddSynagogueForm


class PasswordResetView(MyFormView):
    form = PasswordResetForm

    def save(self, form, *args, **kwargs):
        kwargs['request'] = self.request
        super().save(form, *args, **kwargs)
