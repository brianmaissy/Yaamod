from rest_framework import generics
from django.contrib.auth.models import User
from django.contrib.auth import logout

from webapp.permission import SynagoguePermission, AddUserPermissions
from webapp.models import Synagogue
from webapp.serializers import AddUserSerializer, SynagogueSerializer
from webapp.forms import LoginForm
from django.http import Http404, HttpResponse
from django.views import View
from django.db import transaction


class AtomicPostMixin:
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserCreateAPIView(AtomicPostMixin, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AddUserSerializer
    permission_classes = (AddUserPermissions,)


class SynagogueListCreateView(AtomicPostMixin, generics.ListCreateAPIView):
    queryset = Synagogue.objects.all()
    serializer_class = SynagogueSerializer


class SynagogueDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Synagogue.objects.all()
    serializer_class = SynagogueSerializer
    permission_classes = (SynagoguePermission,)


class LoginView(View):
    def post(self, request):
        form = LoginForm(self.request.POST)
        if not form.is_valid():
            raise Http404()
        form.save(request)
        return HttpResponse()


class LogoutView(View):
    def post(self, request):
        logout(request)
        return HttpResponse()
