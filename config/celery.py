import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# создаём приложение Celery
app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# настраиваем периодические задачи уже ПОСЛЕ создания app
app.conf.beat_schedule = {
    'send-habit-reminders-every-minute': {
        'task': 'habits.tasks.send_habit_reminders',
        'schedule': crontab(),  # каждую минуту
    },
}
