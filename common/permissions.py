from rest_framework.permissions import IsAuthenticated

from common.constants import ADMIN, DIRECTOR, MANAGER


class AdminPermission(IsAuthenticated):
    message = 'Доступ разрешен только админам!'

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.roles == ADMIN


class DirectorPermission(IsAuthenticated):
    message = 'Доступ разрешен только директорам!'

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.roles == DIRECTOR


class ManagerPermission(IsAuthenticated):
    message = 'Доступ разрешен только менеджерам!'

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.roles == MANAGER