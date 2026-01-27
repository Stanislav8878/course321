from django.urls import path
from .views import SaveTelegramChatIdView

urlpatterns = [
    path('save-chat-id/', SaveTelegramChatIdView.as_view(), name='save-chat-id'),
]
