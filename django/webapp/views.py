from rest_framework import generics
from django.contrib.auth.models import User

from webapp.permission import SynagoguePermission
from webapp.models import Synagogue
from webapp.serializers import UserSerializer
from webapp.serializers import SynagogueSerializer


class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SynagogueListCreateView(generics.ListCreateAPIView):
    queryset = Synagogue.objects.all()
    serializer_class = SynagogueSerializer


class SynagogueDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Synagogue.objects.all()
    serializer_class = SynagogueSerializer
    permission_classes = (SynagoguePermission,)
