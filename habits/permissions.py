from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnlyForPublic(BasePermission):
    """
    Пользователь видит свои привычки (CRUD),
    а также публичные (только список/чтение).
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if obj.is_public:
                return True
        return obj.user == request.user
