from django.forms import Form
from django import forms
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login

from webapp.models import Synagogue, get_from_model


class AddUserForm(Form):
    username = forms.CharField()
    password = forms.CharField()
    email = forms.EmailField()

    def add_user(self, group):
        user = User.objects.create_user(self.cleaned_data['username'],
                                        self.cleaned_data['email'],
                                        self.cleaned_data['password'])
        user.groups.add(group)


class AddSynagogueForm(AddUserForm):
    name = forms.CharField()

    def save(self):
        admins = Group.objects.create(name=u'synagogue_{0}_admins'.format(self.cleaned_data['name']))
        Synagogue.objects.create(name=self.cleaned_data['name'], admins=admins)
        self.add_user(admins)


class LoginForm(Form):
    username = forms.CharField()
    password = forms.CharField()

    def save(self, request):
        user = authenticate(request,
                            username=self.cleaned_data['username'], password=self.cleaned_data['password'])
        if user is not None:
            login(self.request, user)
        else:
            raise PermissionDenied()


class AddUserToSynagogueForm(AddUserForm):
    synagogue = forms.IntegerField()

    def save(self):
        synagogue = self.get_synagogue()
        self.add_user(synagogue.admins)

    def get_synagogue(self):
        return get_from_model(Synagogue, pk=self.cleaned_data['synagogue'])
