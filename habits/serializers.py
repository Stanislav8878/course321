from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

    def validate(self, attrs):
        # Дополнительная валидация на уровне DRF (если нужно продублировать)
        instance = Habit(**attrs)
        instance.user = self.context['request'].user
        instance.clean()
        return attrs
