from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny

from habits.models import Habit
from habits.serializers import HabitSerializer
from habits.pagination import DefaultPagination
from habits.permissions import IsOwner


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user).order_by("-id")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PublicHabitsListView(generics.ListAPIView):
    serializer_class = HabitSerializer
    pagination_class = DefaultPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Habit.objects.filter(is_public=True).order_by("-id")
