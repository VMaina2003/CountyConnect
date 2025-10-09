from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Allow access only to Admin users"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'ADMIN')


class IsCountyOfficial(permissions.BasePermission):
    """Allow access only to County Officials"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'EDITOR')


class IsCitizen(permissions.BasePermission):
    """Allow access only to Citizen users"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'WRITER')


class IsViewer(permissions.BasePermission):
    """Allow access only to Viewer users"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'VIEWER')


class AllowUnauthenticated(permissions.BasePermission):
    """
    Allow access to endpoints like register, login, 
    verify email, and password reset without authentication.
    """
    def has_permission(self, request, view):
        return True
class IsCitizenOrCountyOfficialOrAdmin(permissions.BasePermission):
    """
    Allow access to WRITER (Citizen), EDITOR (County Official), or ADMIN roles.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ['WRITER', 'EDITOR', 'ADMIN']
        )
