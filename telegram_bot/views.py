from django.contrib.auth import get_user_model
from rest_framework import permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

User = get_user_model()


class SaveTelegramChatIdSerializer(serializers.Serializer):
    chat_id = serializers.CharField()


class SaveTelegramChatIdView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=SaveTelegramChatIdSerializer,
        responses={200: SaveTelegramChatIdSerializer},
    )
    def post(self, request):
        serializer = SaveTelegramChatIdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        chat_id = serializer.validated_data["chat_id"]

        request.user.telegram_chat_id = chat_id
        request.user.save(update_fields=["telegram_chat_id"])

        return Response(
            {"detail": "Chat ID saved"},
            status=status.HTTP_200_OK,
        )
