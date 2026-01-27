from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()


class SaveTelegramChatIdView(views.APIView):
    """
    POST {"chat_id": "..."} — сохранить chat_id текущему пользователю.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        chat_id = request.data.get('chat_id')
        if not chat_id:
            return Response(
                {'detail': 'chat_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = request.user
        user.telegram_chat_id = chat_id
        user.save()
        return Response({'detail': 'Chat ID saved'}, status=status.HTTP_200_OK)
