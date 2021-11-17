from django.db import models
from rest_framework import permissions

class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.created_by == request.user:
            return True
        return False
        