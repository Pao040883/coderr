from rest_framework import permissions

# Custom permission to allow access only to authenticated users of type 'customer'
class IsCustomerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Grant permission if the user is authenticated and has type 'customer'
        return request.user.is_authenticated and getattr(request.user, 'type', '') == 'customer'


# Custom permission to allow access only to the business user who owns the order
class IsBusinessOrderOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Grant permission if the user is authenticated and is the owner of the business order
        return request.user.is_authenticated and obj.business_user == request.user


# Custom permission to allow access only to admin/staff users
class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        # Grant permission if the user is authenticated and marked as staff
        return request.user.is_authenticated and request.user.is_staff
