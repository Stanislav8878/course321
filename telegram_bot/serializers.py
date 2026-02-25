from rest_framework import serializers


class SaveTelegramChatIdSerializer(serializers.Serializer):
    chat_id = serializers.CharField()