from django.core.exceptions import ValidationError


def validate_reward_or_linked(habit):
    """
    Нельзя одновременно иметь и вознаграждение, и связанную привычку.
    """
    if habit.reward and habit.linked_habit:
        raise ValidationError(
            'Нельзя одновременно указывать вознаграждение и связанную привычку.'
        )


def validate_duration(habit):
    """
    Время выполнения <= 120 секунд.
    """
    if habit.duration and habit.duration > 120:
        raise ValidationError(
            'Время выполнения привычки не может быть больше 120 секунд.'
        )


def validate_linked_is_pleasant(habit):
    """
    В связанные привычки могут попадать только приятные привычки.
    """
    if habit.linked_habit and not habit.linked_habit.is_pleasant:
        raise ValidationError(
            'Связанной может быть только привычка с признаком приятной.'
        )


def validate_pleasant_has_no_reward_or_linked(habit):
    """
    У приятной привычки не может быть вознаграждения или связанной привычки.
    """
    if habit.is_pleasant and (habit.reward or habit.linked_habit):
        raise ValidationError(
            'У приятной привычки не должно быть вознаграждения или связанной привычки.'
        )


def validate_periodicity(habit):
    """
    Нельзя выполнять привычку реже, чем один раз в 7 дней.
    """
    if habit.periodicity and habit.periodicity > 7:
        raise ValidationError(
            'Периодичность не может быть больше 7 дней.'
        )
