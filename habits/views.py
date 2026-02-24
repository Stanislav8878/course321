from rest_framework import generics, viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from habits.models import Habit
from habits.permissions import IsOwner
from habits.serializers import HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    """
    CRUD привычек текущего пользователя.
    """
    serializer_class = HabitSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, IsOwner)

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user).order_by("-id")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PublicHabitsListView(generics.ListAPIView):
    """
    Публичные привычки доступны ВСЕМ (без авторизации)
    """
    serializer_class = HabitSerializer
    queryset = Habit.objects.filter(is_public=True).order_by("-id")

    # 🔥 ВОТ ЭТО КЛЮЧЕВОЕ
    permission_classes = [permissions.AllowAny]
