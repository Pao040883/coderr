from rest_framework import permissions


# Custom permission to check if the user is a business user
class IsBusinessUser(permissions.BasePermission):
    # This method checks general permission before accessing the view
    def has_permission(self, request, view):
        # Allow access only if the user is authenticated and has type 'business'
        return request.user.is_authenticated and getattr(request.user, 'type', '') == 'business'


# Custom permission to ensure that the requesting user is the owner of the object
class IsOwner(permissions.BasePermission):
    # This method checks object-level permissions (e.g. for detail views)
    def has_object_permission(self, request, view, obj):
        # Allow access only if the object belongs to the requesting user
        return obj.user == request.user
