from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import HabitViewSet, PublicHabitListView

router = DefaultRouter()
router.register(r"", HabitViewSet, basename="habit")

urlpatterns = [
    path("public/", PublicHabitListView.as_view(), name="public-habits"),
    path("", include(router.urls)),
]
