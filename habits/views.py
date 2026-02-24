from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from habits.models import Habit
from habits.pagination import HabitPagination
from habits.permissions import IsOwner
from habits.serializers import HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    pagination_class = HabitPagination

    def get_queryset(self):
        # только привычки текущего пользователя
        return Habit.objects.filter(user=self.request.user).order_by("-id")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PublicHabitsListView(ListAPIView):
    serializer_class = HabitSerializer
    permission_classes = [AllowAny]  # важно: публичный список без авторизации
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(is_public=True).order_by("-id")

