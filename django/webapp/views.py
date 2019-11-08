from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.views import View
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.utils.decorators import method_decorator


from webapp.permission import SynagoguePermission, AddUserPermissions, GetAddMemberTokenPermissions
from webapp.models import Synagogue
from webapp.serializers import AddUserSerializer, SynagogueSerializer, LoginSerializer, GetAddMemberTokenSerializer

from functools import wraps


def atomic_wrapper(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        with transaction.atomic():
            return f(*args, **kwargs)
    return wrapper


@method_decorator(atomic_wrapper, name='post')
class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AddUserSerializer
    permission_classes = (AddUserPermissions,)


@method_decorator(atomic_wrapper, name='post')
class SynagogueListCreateView(generics.ListCreateAPIView):
    queryset = Synagogue.objects.all()
    serializer_class = SynagogueSerializer


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


class GetAddMemberTokenView(APIView):
    permission_classes = (GetAddMemberTokenPermissions,)

    def post(self, request):
        serializer = GetAddMemberTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        synagogue = serializer.validated_data['synagogue']
        token, created = Token.objects.get_or_create(user=synagogue.member_creator)
        return Response({'token': token.key})
