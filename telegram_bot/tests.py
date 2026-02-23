import types
from importlib import reload

import pytest
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from telegram_bot import utils

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_save_telegram_chat_id_requires_auth(api_client):
    """
    Без авторизации эндпоинт должен вернуть 401.
    """
    response = api_client.post(
        '/api/telegram/save-chat-id/',
        data={'chat_id': '12345'},
        format='json',
    )
    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_save_telegram_chat_id_success(api_client):
    """
    Авторизованный пользователь может сохранить свой chat_id.
    """
    user = User.objects.create_user(username='tguser', password='12345')
    api_client.force_authenticate(user=user)

    response = api_client.post(
        '/api/telegram/save-chat-id/',
        data={'chat_id': '999888'},
        format='json',
    )
    assert response.status_code == 200

    user.refresh_from_db()
    assert user.telegram_chat_id == '999888'


@pytest.mark.django_db
def test_send_telegram_message(monkeypatch):
    """
    Тестируем функцию отправки сообщения в Telegram без реального HTTP.
    """
    # подменяем токен в окружении
    monkeypatch.setenv('TELEGRAM_BOT_TOKEN', 'TEST_TOKEN')
    reload(utils)  # перечитать модуль, чтобы подтянуть новый токен

    called = {}

    def fake_post(url, data, timeout):
        called['url'] = url
        called['data'] = data
        called['timeout'] = timeout

    # подменяем requests.post внутри модуля utils
    monkeypatch.setattr(utils, 'requests', types.SimpleNamespace(post=fake_post))

    utils.send_telegram_message('123', 'hello')

    assert 'botTEST_TOKEN' in called['url']
    assert called['data']['chat_id'] == '123'
    assert called['data']['text'] == 'hello'
    assert called['timeout'] == 10
