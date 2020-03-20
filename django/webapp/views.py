from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.transaction import atomic
from django.utils.decorators import method_decorator
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from webapp.models import Synagogue, Person
from webapp.permission import PostSynagoguePermission, IsGetOrAuthenticated
from webapp.serializers import UserSerializer, SynagogueSerializer, LoginSerializer, PersonSerializer
from webapp.filters import FilterSynagogueBackend
from webapp.utils import request_to_synagogue


@method_decorator(atomic, name='dispatch')
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@method_decorator(atomic, name='dispatch')
class SynagogueListCreateView(generics.ListCreateAPIView):
    queryset = Synagogue.objects.all()
    serializer_class = SynagogueSerializer
    # an authenticated user must be logged in on creation to be put in the admins group
    permission_classes = (IsGetOrAuthenticated,)


class SynagogueDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Synagogue.objects.all()
    serializer_class = SynagogueSerializer
    permission_classes = (PostSynagoguePermission,)


class PersonListCreateView(generics.ListCreateAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filter_backends = (FilterSynagogueBackend,)


class PersonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filter_backends = (FilterSynagogueBackend,)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(request, **serializer.validated_data)
        if user is not None:
            login(request, user)
        else:
            raise PermissionDenied()

        return Response()


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response()


class MakeAddMemberTokenView(APIView):
    def post(self, request):
        synagogue = request_to_synagogue(request)
        token, created = Token.objects.get_or_create(user=synagogue.member_creator)
        return Response({'token': token.key})
