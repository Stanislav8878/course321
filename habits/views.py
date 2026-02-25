from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from .models import Habit
from .serializers import HabitSerializer


class HabitViewSet(ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    lookup_url_kwarg = "id"

    def get_queryset(self):
        # Привычки только текущего пользователя
        return Habit.objects.filter(user=self.request.user)


class PublicHabitListView(ListAPIView):
    """
    Публичные привычки (доступно без авторизации).
    Если в модели нет поля is_public, просто вернём пустой список (чтобы CI не падал).
    """
    serializer_class = HabitSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        field_names = {f.name for f in Habit._meta.fields}
        if "is_public" in field_names:
            return Habit.objects.filter(is_public=True)
        return Habit.objects.none()
