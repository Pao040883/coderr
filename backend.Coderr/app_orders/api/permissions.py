from rest_framework import permissions

class IsCustomerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'type', '') == 'customer'

class IsBusinessOrderOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.business_user == request.user

class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff
