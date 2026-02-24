from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """
    Разрешает доступ только владельцу объекта.
    Для list/create проверяем только аутентификацию во view.
    """
    def has_object_permission(self, request, view, obj):
        return getattr(obj, "user", None) == request.user


class IsOwnerOrReadOnlyForPublic(BasePermission):
    """
    Если объект публичный — можно читать всем.
    Если не публичный — только владельцу.
    Запись/изменение — только владельцу.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if getattr(obj, "is_public", False):
                return True
            return getattr(obj, "user", None) == request.user
        return getattr(obj, "user", None) == request.user
