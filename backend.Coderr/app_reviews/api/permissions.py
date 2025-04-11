from rest_framework import permissions

# Custom permission: allows access only to authenticated users of type 'customer'
class IsCustomerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Grant permission if the user is authenticated and has type 'customer'
        return request.user.is_authenticated and getattr(request.user, 'type', '') == 'customer'


# Custom permission: allows access only to the user who created (reviewed) the object
class IsReviewer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Grant permission if the user is the reviewer of the object
        return obj.reviewer == request.user
