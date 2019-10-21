from django.contrib.auth.models import Group
from rest_framework import permissions
import abc


class InSynagogueAdminsPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        synagogue = self.get_synagogue(obj)

        try:
            request.user.groups.get(pk=synagogue.admins.pk)
        except Group.DoesNotExist:
            return False
        else:
            return True

    @abc.abstractmethod
    def get_synagogue(self, obj):
        pass


class SynagoguePermission(InSynagogueAdminsPermission):
    def get_synagogue(self, obj):
        return obj
