from datetime import datetime, timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from telegram_bot.utils import send_telegram_message

from .models import Habit


def _is_due_for_notification(habit: Habit, now: datetime) -> bool:
    """Проверяем, нужно ли прислать напоминание прямо сейчас.

    Логика простая и практичная:
    - сравниваем время привычки с текущим временем с точностью до минуты;
    - не шлём чаще, чем раз в periodicity дней.
    """

    if habit.time.hour != now.time().hour or habit.time.minute != now.time().minute:
        return False

    last = habit.last_notified_at
    if last is None:
        return True

    # Разрешаем следующее уведомление после periodicity дней
    next_allowed = last + timedelta(days=habit.periodicity)
    return now >= next_allowed


@shared_task
def send_habit_reminders():
    """Периодическая задача (каждую минуту) — рассылает напоминания в Telegram."""

    if not getattr(settings, "TELEGRAM_BOT_TOKEN", ""):
        return "TELEGRAM_BOT_TOKEN is empty"

    now = timezone.localtime(timezone.now())

    # Берём только тех, у кого есть chat_id
    habits = (
        Habit.objects.select_related("user", "related_habit")
        .filter(user__telegram_chat_id__isnull=False)
        .exclude(user__telegram_chat_id="")
    )

    sent = 0
    for habit in habits:
        if not _is_due_for_notification(habit, now):
            continue

        reward = ""
        if habit.related_habit:
            reward = f"\nПосле выполнения: {habit.related_habit.action}"
        elif habit.reward:
            reward = f"\nВознаграждение: {habit.reward}"

        text = (
            f"Напоминание о привычке:\n"
            f"Действие: {habit.action}\n"
            f"Когда: {habit.time.strftime('%H:%M')}\n"
            f"Где: {habit.place}"
            f"{reward}"
        )

        try:
            send_telegram_message(habit.user.telegram_chat_id, text)
            habit.last_notified_at = now
            habit.save(update_fields=["last_notified_at"])
            sent += 1
        except Exception:
            # Не падаем всей задачей из-за одной ошибки
            continue

    return f"sent={sent}"
