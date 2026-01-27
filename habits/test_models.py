import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from habits.models import Habit

User = get_user_model()


@pytest.mark.django_db
def test_habit_cannot_have_reward_and_linked():
    """
    Нельзя одновременно указывать вознаграждение и связанную привычку.
    """
    user = User.objects.create_user(username='test', password='12345')
    pleasant = Habit.objects.create(
        user=user,
        place='Дом',
        time='10:00',
        action='Почитать книгу',
        is_pleasant=True,
        duration=60,
    )

    habit = Habit(
        user=user,
        place='Улица',
        time='11:00',
        action='Пробежка',
        linked_habit=pleasant,
        reward='Шоколадка',
        duration=60,
    )
    with pytest.raises(ValidationError):
        habit.full_clean()


@pytest.mark.django_db
def test_habit_duration_cannot_be_more_than_120():
    """
    Время выполнения должно быть не больше 120 секунд.
    """
    user = User.objects.create_user(username='user_duration', password='12345')

    habit = Habit(
        user=user,
        place='Дом',
        time='09:00',
        action='Сделать зарядку',
        duration=121,
    )

    with pytest.raises(ValidationError):
        habit.full_clean()


@pytest.mark.django_db
def test_linked_habit_must_be_pleasant():
    """
    В связанные привычки могут попадать только приятные привычки.
    """
    user = User.objects.create_user(username='user_linked', password='12345')

    not_pleasant = Habit.objects.create(
        user=user,
        place='Дом',
        time='08:00',
        action='Уборка квартиры',
        is_pleasant=False,
        duration=60,
    )

    habit = Habit(
        user=user,
        place='Дом',
        time='08:30',
        action='Полить цветы',
        linked_habit=not_pleasant,
        duration=60,
    )

    with pytest.raises(ValidationError):
        habit.full_clean()


@pytest.mark.django_db
def test_pleasant_habit_cannot_have_reward_or_linked():
    """
    У приятной привычки не может быть вознаграждения или связанной привычки.
    """
    user = User.objects.create_user(username='user_pleasant', password='12345')

    habit = Habit(
        user=user,
        place='Дом',
        time='20:00',
        action='Играть в игру',
        is_pleasant=True,
        reward='Печенька',
        duration=60,
    )

    with pytest.raises(ValidationError):
        habit.full_clean()


@pytest.mark.django_db
def test_periodicity_not_more_than_seven_days():
    """
    Нельзя выполнять привычку реже, чем раз в 7 дней.
    """
    user = User.objects.create_user(username='user_periodicity', password='12345')

    habit = Habit(
        user=user,
        place='Дом',
        time='21:00',
        action='Заниматься английским',
        periodicity=8,
        duration=60,
    )

    with pytest.raises(ValidationError):
        habit.full_clean()


@pytest.mark.django_db
def test_valid_habit_saves_successfully():
    """
    Корректная привычка проходит все валидаторы и сохраняется.
    """
    user = User.objects.create_user(username='user_ok', password='12345')

    habit = Habit.objects.create(
        user=user,
        place='Дом',
        time='22:00',
        action='Читать книгу 10 минут',
        duration=120,
        periodicity=1,
        is_pleasant=False,
        reward='Чашка чая',
        is_public=True,
    )

    assert habit.id is not None
    assert habit.is_public is True
