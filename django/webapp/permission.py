from django.contrib.auth.models import Group
from rest_framework import permissions
import abc

from webapp.serializers import UserSerializer, MakeAddMemberTokenSerializer


def _check_request_for_synagogue(request, synagogue):
    try:
        request.user.groups.get(pk=synagogue.admins.pk)
    except Group.DoesNotExist:
        return False
    else:
        return True


class SynagoguePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return _check_request_for_synagogue(request, obj)


class SerializerPermissions(permissions.BasePermission):
    @property
    @classmethod
    @abc.abstractmethod
    def serializer(cls):
        pass

    def has_permission(self, request, view):
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.needs_synagogue_check():
            return True
        return _check_request_for_synagogue(request, serializer.get_synagogue())


class AddUserPermissions(SerializerPermissions):
    serializer = UserSerializer


class MakeAddMemberTokenPermissions(SerializerPermissions):
    serializer = MakeAddMemberTokenSerializer
