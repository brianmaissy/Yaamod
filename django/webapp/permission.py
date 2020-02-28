from rest_framework import permissions
from webapp.utils import request_to_synagogue


class IsGetOrAuthenticated(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return super().has_permission(request, view)


class SynagoguePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request_to_synagogue(request) == obj


class PostSynagoguePermission(SynagoguePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        return super().has_object_permission(request, view, obj)
