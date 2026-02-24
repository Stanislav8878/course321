from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """
    Разрешает доступ только владельцу объекта.
    """

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "user_id", None) == getattr(request.user, "id", None)


class IsOwnerOrReadOnly(BasePermission):
    """
    Чтение всем, изменение только владельцу.
    (на всякий случай, если понадобится)
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, "user_id", None) == getattr(request.user, "id", None)
