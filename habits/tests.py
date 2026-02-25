from datetime import time

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from .models import Habit


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_habit_validators_reward_and_related_conflict(api_client):
    user = User.objects.create_user(username="u1", password="pass")
    api_client.force_authenticate(user=user)

    pleasant = Habit.objects.create(
        user=user,
        place="home",
        time=time(9, 0),
        action="take a bath",
        is_pleasant=True,
        periodicity=1,
        duration=60,
    )

    payload = {
        "place": "park",
        "time": "10:00:00",
        "action": "walk",
        "is_pleasant": False,
        "related_habit": pleasant.id,
        "reward": "cake",
        "periodicity": 1,
        "duration": 60,
        "is_public": False,
    }
    resp = api_client.post("/api/habits/", data=payload, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_public_habits_read_only(api_client):
    u1 = User.objects.create_user(username="u1", password="pass")
    u2 = User.objects.create_user(username="u2", password="pass")
    Habit.objects.create(
        user=u1,
        place="home",
        time=time(9, 0),
        action="pushups",
        is_pleasant=False,
        periodicity=1,
        duration=60,
        is_public=True,
        reward="tea",
    )

    resp = api_client.get("/api/habits/public/")
    assert resp.status_code == 200
    assert resp.data["count"] == 1

    api_client.force_authenticate(user=u2)
    resp2 = api_client.post("/api/habits/public/", data={"x": 1}, format="json")
    assert resp2.status_code in (401, 403, 405)
