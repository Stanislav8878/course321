import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_create_user_model():
    """
    Проверяем кастомную модель пользователя и поле telegram_chat_id.
    """
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='12345',
        telegram_chat_id='999',
    )
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.telegram_chat_id == '999'
    assert user.check_password('12345')


@pytest.mark.django_db
def test_register_endpoint(api_client):
    """
    Регистрация через /api/users/register/.
    """
    response = api_client.post(
        '/api/users/register/',
        data={
            'username': 'apiuser',
            'email': 'api@example.com',
            'password': '12345',
        },
        format='json',
    )
    assert response.status_code == 201
    assert User.objects.filter(username='apiuser').exists()
