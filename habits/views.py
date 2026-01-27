from rest_framework import viewsets, generics, permissions
from .models import Habit
from .serializers import HabitSerializer
from .permissions import IsOwnerOrReadOnlyForPublic


class HabitViewSet(viewsets.ModelViewSet):
    """
    CRUD привычек текущего пользователя с пагинацией.
    """
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnlyForPublic]

    def get_queryset(self):
        # Только свои привычки
        return Habit.objects.filter(user=self.request.user).order_by('-created_at')


class PublicHabitsListView(generics.ListAPIView):
    """
    Список публичных привычек (только чтение).
    """
    serializer_class = HabitSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Habit.objects.filter(is_public=True).order_by('-created_at')
