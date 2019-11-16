from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.transaction import atomic
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from webapp.models import Synagogue
from webapp.permission import SynagoguePermission, AddUserPermissions, MakeAddMemberTokenPermissions, \
    IsGetOrAuthenticated
from webapp.serializers import UserSerializer, SynagogueSerializer, LoginSerializer, MakeAddMemberTokenSerializer


@method_decorator(atomic, name='dispatch')
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AddUserPermissions,)


@method_decorator(atomic, name='dispatch')
class SynagogueListCreateView(generics.ListCreateAPIView):
    queryset = Synagogue.objects.all()
    serializer_class = SynagogueSerializer
    # an authenticated user must be logged in on creation to be put in the admins group
    permission_classes = (IsGetOrAuthenticated,)


class SynagogueDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Synagogue.objects.all()
    serializer_class = SynagogueSerializer
    permission_classes = (SynagoguePermission,)


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


class LogoutView(View):
    def post(self, request):
        logout(request)
        return HttpResponse()


class MakeAddMemberTokenView(APIView):
    permission_classes = (MakeAddMemberTokenPermissions,)

    def post(self, request):
        serializer = MakeAddMemberTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        synagogue = serializer.validated_data['synagogue']
        token, created = Token.objects.get_or_create(user=synagogue.member_creator)
        return Response({'token': token.key})
