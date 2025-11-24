from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth.models import Group


def in_group(user, group_name):
    if not user or not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()


def _conductor_owns_furgon(user, obj):
    """Return True if the given user has a conductor_profile that matches obj.conductor."""
    try:
        conductor_profile = getattr(user, 'conductor_profile', None)
        if conductor_profile and hasattr(obj, 'conductor') and obj.conductor and getattr(obj.conductor, 'pk', None) == getattr(conductor_profile, 'pk', None):
            return True
    except Exception:
        return False
    return False


def _apoderado_owns_student(user, obj):
    """Return True if the given user is the apoderado_user of the student object."""
    try:
        if getattr(obj, 'apoderado_user', None) and getattr(obj.apoderado_user, 'pk', None) == getattr(user, 'pk', None):
            return True
    except Exception:
        return False
    return False


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        # Admins full
        if request.user and (request.user.is_staff or in_group(request.user, 'Administrador')):
            return True
        # Allow authenticated apoderado or conductor to proceed to object-level checks
        if request.user and in_group(request.user, 'Apoderado'):
            return True
        if request.user and in_group(request.user, 'Conductor'):
            return True
        return False


class IsAdminOrConductorOrReadOnly(BasePermission):
    """Permite escritura a Admin; lectura a todos; acciones específicas permitidas a Conductores sobre sus recursos."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        # Admins full
        if request.user and (request.user.is_staff or in_group(request.user, 'Administrador')):
            return True
        # Allow conductors to call specific actions (e.g. update_location)
        if request.user and in_group(request.user, 'Conductor'):
            action = getattr(view, 'action', None)
            if action in ('update_location',):
                return True
        return False

    def has_object_permission(self, request, view, obj):
        # Lectura siempre permitida
        if request.method in SAFE_METHODS:
            return True
        # Admins full
        if request.user and (request.user.is_staff or in_group(request.user, 'Administrador')):
            return True
        # Allow conductor to update only the location action on their own furgon
        if in_group(request.user, 'Conductor'):
            action = getattr(view, 'action', None)
            if _conductor_owns_furgon(request.user, obj) and action in ('update_location',):
                return True
        return False


class IsAdminOrApoderadoOrConductorOrReadOnly(BasePermission):
    """For student resources: Admin full; Apoderado can read/write own student's records; Conductor can read students assigned to his furgon."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and (request.user.is_staff or in_group(request.user, 'Administrador'))

    def has_object_permission(self, request, view, obj):
        # obj expected to be Estudiante
        if request.method in SAFE_METHODS:
            # Conductor can read students assigned to their furgones
            user = request.user
            if user and in_group(user, 'Conductor'):
                if _conductor_owns_furgon(user, getattr(obj, 'furgon', None)):
                    return True
            # Apoderado can view their own students
            if user and in_group(user, 'Apoderado'):
                if _apoderado_owns_student(user, obj):
                    return True
            # allow public read (IsAuthenticatedOrReadOnly handled elsewhere) - keep False here to rely on global
            return True
        # Writes: only Admin or Apoderado (owner)
        if request.user and (request.user.is_staff or in_group(request.user, 'Administrador')):
            return True
        if request.user and in_group(request.user, 'Apoderado'):
            if _apoderado_owns_student(request.user, obj):
                return True
        return False


class AllowAuthenticatedWriteOrReadOnly(BasePermission):
    """Allow read-only for everyone, but require authentication for write actions.

    This is intentionally permissive at the view-level; views should perform stricter
    object-level ownership checks where needed.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
