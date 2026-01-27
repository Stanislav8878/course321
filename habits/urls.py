from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HabitViewSet, PublicHabitsListView

router = DefaultRouter()
router.register('habits', HabitViewSet, basename='habit')

urlpatterns = [
    path('', include(router.urls)),
    path('habits/public/', PublicHabitsListView.as_view(), name='public-habits'),
]
