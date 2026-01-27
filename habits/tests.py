import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from habits.models import Habit
from habits.tasks import send_habit_reminders

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_habit_crud_flow(api_client):
    """
    Полный CRUD сценарий для привычки текущего пользователя.
    """
    user = User.objects.create_user(username='crud_user', password='12345')
    api_client.force_authenticate(user=user)

    # CREATE
    response = api_client.post(
        '/api/habits/',
        data={
            'place': 'Дом',
            'time': '10:00',
            'action': 'Читать книгу',
            'duration': 60,
            'periodicity': 1,
            'is_public': False,
        },
        format='json',
    )
    assert response.status_code == 201
    habit_id = response.data['id']

    # LIST
    response = api_client.get('/api/habits/')
    assert response.status_code == 200
    assert len(response.data['results']) == 1

    # RETRIEVE
    response = api_client.get(f'/api/habits/{habit_id}/')
    assert response.status_code == 200
    assert response.data['action'] == 'Читать книгу'

    # UPDATE (PATCH)
    response = api_client.patch(
        f'/api/habits/{habit_id}/',
        data={'action': 'Читать техническую книгу'},
        format='json',
    )
    assert response.status_code == 200
    assert response.data['action'] == 'Читать техническую книгу'

    # DELETE
    response = api_client.delete(f'/api/habits/{habit_id}/')
    assert response.status_code == 204
    assert Habit.objects.count() == 0


@pytest.mark.django_db
def test_public_habits_list(api_client):
    """
    Публичные привычки видны всем, приватные не попадают в список.
    """
    user1 = User.objects.create_user(username='u1', password='12345')
    user2 = User.objects.create_user(username='u2', password='12345')

    Habit.objects.create(
        user=user1,
        place='Дом',
        time='09:00',
        action='Полить цветы',
        duration=60,
        is_public=True,
    )
    Habit.objects.create(
        user=user2,
        place='Улица',
        time='10:00',
        action='Пробежка',
        duration=60,
        is_public=False,
    )

    response = api_client.get('/api/habits/public/')
    assert response.status_code == 200
    # в списке только одна публичная привычка
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['action'] == 'Полить цветы'


@pytest.mark.django_db
def test_user_cannot_see_another_user_habit(api_client):
    """
    Пользователь не видит чужие привычки в своём CRUD-эндоинте.
    """
    owner = User.objects.create_user(username='owner', password='12345')
    other = User.objects.create_user(username='other', password='12345')

    habit = Habit.objects.create(
        user=owner,
        place='Дом',
        time='12:00',
        action='Делать зарядку',
        duration=60,
    )

    api_client.force_authenticate(user=other)
    response = api_client.get(f'/api/habits/{habit.id}/')
    # т.к. queryset фильтруется по request.user, будет 404
    assert response.status_code == 404


@pytest.mark.django_db
def test_send_habit_reminders(monkeypatch, settings):
    """
    Тест Celery-задачи отправки напоминаний.
    """
    user = User.objects.create_user(
        username='user_reminder',
        password='12345',
        telegram_chat_id='123456',
    )

    now = timezone.localtime()
    habit = Habit.objects.create(
        user=user,
        place='Дом',
        time=now.time().replace(second=0, microsecond=0),
        action='Сделать растяжку',
        duration=60,
    )

    called = {}

    def fake_send(chat_id, text):
        called['chat_id'] = chat_id
        called['text'] = text

    # патчим send_telegram_message внутри модуля tasks
    monkeypatch.setattr('habits.tasks.send_telegram_message', fake_send)

    # вызываем .run(), чтобы выполнить тело задачи синхронно
    send_habit_reminders.run()

    assert called.get('chat_id') == user.telegram_chat_id
    assert habit.action in called.get('text', '')
