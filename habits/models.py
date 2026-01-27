from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

from . import validators


class Habit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habits'
    )
    place = models.CharField(max_length=255)
    time = models.TimeField()
    action = models.CharField(max_length=255)

    is_pleasant = models.BooleanField(default=False)

    linked_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_to',
        help_text='Связанная приятная привычка'
    )

    periodicity = models.PositiveSmallIntegerField(
        default=1,
        help_text='Периодичность выполнения в днях (по умолчанию 1)'
    )

    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Вознаграждение за выполнение привычки'
    )

    duration = models.PositiveIntegerField(
        help_text='Время на выполнение в секундах',
        default=60
    )

    is_public = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        errors = []
        try:
            validators.validate_reward_or_linked(self)
        except ValidationError as e:
            errors.extend(e.error_list)

        try:
            validators.validate_duration(self)
        except ValidationError as e:
            errors.extend(e.error_list)

        try:
            validators.validate_linked_is_pleasant(self)
        except ValidationError as e:
            errors.extend(e.error_list)

        try:
            validators.validate_pleasant_has_no_reward_or_linked(self)
        except ValidationError as e:
            errors.extend(e.error_list)

        try:
            validators.validate_periodicity(self)
        except ValidationError as e:
            errors.extend(e.error_list)

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.action} ({self.user})'
