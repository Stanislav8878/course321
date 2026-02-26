import types

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_save_telegram_chat_id_requires_auth(api_client):
    response = api_client.post("/api/telegram/save-chat-id/", data={"chat_id": "12345"}, format="json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_save_telegram_chat_id_success(api_client):
    user = User.objects.create_user(username="tguser", password="999888")
    api_client.force_authenticate(user=user)
    response = api_client.post("/api/telegram/save-chat-id/", data={"chat_id": "12345"}, format="json")
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.telegram_chat_id == "12345"


def test_send_telegram_message(monkeypatch):
    """Тестируем функцию отправки сообщения в Telegram без реального HTTP."""

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "TEST_TOKEN")

    # Переимпорт, чтобы подхватить env
    from importlib import reload
    import telegram_bot.utils as utils

    reload(utils)

    called = {}

    def fake_post(url, data=None, timeout=None):
        called["url"] = url
        called["data"] = data
        called["timeout"] = timeout
        return types.SimpleNamespace(status_code=200, text="ok")

    monkeypatch.setattr(utils, "requests", types.SimpleNamespace(post=fake_post))
    resp = utils.send_telegram_message("123", "hello")

    assert "botTEST_TOKEN" in called["url"]
    assert called["data"]["chat_id"] == "123"
    assert called["data"]["text"] == "hello"
    assert called["timeout"] == 10
    assert resp.status_code == 200
