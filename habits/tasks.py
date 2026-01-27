from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Habit
from telegram_bot.utils import send_telegram_message

User = get_user_model()


@shared_task
def send_habit_reminders():
    """
    Пример: отправить напоминания о привычках,
    у которых время == текущему часу/минуте.
    (Можно усложнить логику по periodicity).
    """
    now = timezone.localtime()
    habits = Habit.objects.filter(time__hour=now.hour, time__minute=now.minute)

    for habit in habits:
        user = habit.user
        if not user.telegram_chat_id:
            continue

        text = (
            f'Напоминание о привычке:\n'
            f'{habit.action} в {habit.time.strftime("%H:%M")} в {habit.place}'
        )
        send_telegram_message(user.telegram_chat_id, text)
