from rest_framework import serializers


def validate_habit_payload(attrs):
    """Валидаторы из ТЗ (одним местом, чтобы переиспользовать в create/update)."""

    reward = attrs.get("reward")
    related_habit = attrs.get("related_habit")
    is_pleasant = attrs.get("is_pleasant")
    duration = attrs.get("duration")
    periodicity = attrs.get("periodicity")

    # 1) Нельзя одновременно reward и related_habit
    if reward and related_habit:
        raise serializers.ValidationError(
            {"non_field_errors": ["Нельзя одновременно указать вознаграждение и связанную привычку."]}
        )

    # 2) Время выполнения <= 120 секунд
    if duration is not None and duration > 120:
        raise serializers.ValidationError({"duration": "Время выполнения не должно превышать 120 секунд."})

    # 3) Периодичность 1..7
    if periodicity is not None and not (1 <= periodicity <= 7):
        raise serializers.ValidationError({"periodicity": "Нельзя выполнять привычку реже, чем 1 раз в 7 дней."})

    # 4) В связанные привычки — только приятные
    if related_habit is not None and not related_habit.is_pleasant:
        raise serializers.ValidationError({"related_habit": "Связанная привычка должна быть приятной."})

    # 5) У приятной привычки не может быть reward или related_habit
    if is_pleasant:
        if reward:
            raise serializers.ValidationError({"reward": "У приятной привычки не может быть вознаграждения."})
        if related_habit:
            raise serializers.ValidationError({"related_habit": "У приятной привычки не может быть связанной привычки."})

    return attrs
