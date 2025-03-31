from rest_framework import permissions

class IsCustomerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'type', '') == 'customer'

class IsReviewer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user
