from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from .models import Habit
from .serializers import HabitSerializer


class HabitViewSet(ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    lookup_url_kwarg = "id"

    def get_queryset(self):
        # Добавляем фильтрацию по пользователю
        user = self.request.user
        return Habit.objects.filter(user=user)