from django.contrib.auth.models import Group
from rest_framework import permissions

from webapp.serializers import AddUserSerializer


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


class AddUserPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        serializer = AddUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return _check_request_for_synagogue(request, serializer.validated_data['synagogue'])
