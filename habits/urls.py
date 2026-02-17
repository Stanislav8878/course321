from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HabitViewSet, PublicHabitsListView

router = DefaultRouter()
router.register('habits', HabitViewSet, basename='habit')

urlpatterns = [
    # ВАЖНО: сначала public, потом router, иначе router перехватывает "public" как pk
    path('habits/public/', PublicHabitsListView.as_view(), name='public-habits'),
    path('', include(router.urls)),
]
