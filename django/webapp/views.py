import abc

from django.contrib.auth import logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import Group
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse
from django.views.generic import DetailView, ListView, View
from django.db import transaction

from webapp.forms import AddUserAndSynagogue, LoginForm, AddUserToSynagogueForm
from webapp.models import Synagogue, Member, get_from_model


class SynagoguePermissionChecker(UserPassesTestMixin):
    """
    an abstract class to check if the user has admin permissions for the requested synagogue.
    every child class need to implement get_synagogue which get the synagogue we are trying to query about
    from the request. It will return 403 if he is unauthorized.
    This class should be the first to inherit from.
    """
    raise_exception = True

    def test_func(self):
        synagogue = self.get_synagogue()
        try:
            self.request.user.groups.get(pk=synagogue.admins.pk)
        except Group.DoesNotExist:
            return False
        else:
            return True

    @abc.abstractmethod
    def get_synagogue(self):
        pass


class PostFormView(View):
    """
    django's FormView is not what we need since it does a lot that we don't need (e.g implement a GET that render
    template, but we only want a simple post). So this simple FormView is exactly what we need. it is separated to
    a lot of functions to let the children hook it. The usual child should just add
    form = <MyForm>
    and let the form do all the job.
    """
    include_request = False

    @property
    @classmethod
    @abc.abstractmethod
    def form(cls):
        pass

    @transaction.atomic
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

    def save(self, form):
        kwargs = {}
        if self.include_request:
            kwargs['request'] = self.request
        form.save(**kwargs)


def safe_get(data, *names):
    """
    get some properties from dict safely (raise 400 if it is not there)
    """
    args = []
    for name in names:
        arg = data.get(name)
        if arg is None:
            raise SuspiciousOperation()
        args.append(arg)
    if len(args) == 1:
        args = args[0]
    return args


class SynagoguePermissionCheckFormView(SynagoguePermissionChecker, PostFormView, abc.ABC):
    def get_synagogue(self):
        form = self.get_form()
        return form.get_synagogue()


class SynagogueList(ListView):
    def get_queryset(self):
        return Synagogue.objects.filter(
            admins__in=self.request.user.groups.all())


class SynagogueDetail(SynagoguePermissionChecker, DetailView):
    model = Synagogue

    def get_synagogue(self):
        pk = safe_get(self.kwargs, 'pk')
        return get_from_model(Synagogue, pk=pk)


class MemberDetail(SynagoguePermissionChecker, DetailView):
    model = Member

    def get_synagogue(self):
        member_pk = safe_get(self.kwargs, 'pk')
        member = get_from_model(Member, pk=member_pk)
        return member.synagogue


class LoginView(PostFormView):
    form = LoginForm
    include_request = True


class LogoutView(View):
    def post(self, request):
        logout(request)
        return HttpResponse()


class AddUserView(SynagoguePermissionCheckFormView):
    form = AddUserToSynagogueForm


class AddSynagogueView(PostFormView):
    form = AddUserAndSynagogue


class PasswordResetView(PostFormView):
    form = PasswordResetForm
    include_request = True
