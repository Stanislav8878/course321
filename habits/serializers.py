from rest_framework import serializers

from .models import Habit
from .validators import validate_habit_payload


class HabitSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Habit
        fields = (
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "duration",
            "is_public",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def validate(self, attrs):
        # На update часть полей может отсутствовать — подмешиваем текущие значения
        if self.instance is not None:
            merged = {
                "reward": attrs.get("reward", self.instance.reward),
                "related_habit": attrs.get("related_habit", self.instance.related_habit),
                "is_pleasant": attrs.get("is_pleasant", self.instance.is_pleasant),
                "duration": attrs.get("duration", self.instance.duration),
                "periodicity": attrs.get("periodicity", self.instance.periodicity),
            }
            # дополняем остальными ключами, если есть
            merged.update(attrs)
            return validate_habit_payload(merged)

        return validate_habit_payload(attrs)


class PublicHabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = (
            "id",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "duration",
        )
