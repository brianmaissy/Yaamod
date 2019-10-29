from django.forms import Form
from django import forms
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login


class LoginForm(Form):
    username = forms.CharField()
    password = forms.CharField()

    def save(self, request):
        user = authenticate(request,
                            username=self.cleaned_data['username'], password=self.cleaned_data['password'])
        if user is not None:
            login(request, user)
        else:
            raise PermissionDenied()
