"""Тесты для API подписок на пользователей."""

import pytest
from recipes.models import Subscription
from rest_framework import status


@pytest.mark.django_db
class TestSubscriptionAPI:
    """Тестирование подписки и отписки на авторов."""

    def test_subscribe_self(self, auth_client, user):
        """Подписка на самого себя возвращает 400."""
        url = f'/api/users/{user.id}/subscribe/'
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_subscribe_twice(self, auth_client, another_user):
        """Повторная подписка на того же автора возвращает 400."""
        url = f'/api/users/{another_user.id}/subscribe/'
        response1 = auth_client.post(url)
        assert response1.status_code == status.HTTP_201_CREATED
        response2 = auth_client.post(url)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_subscribe_success(self, auth_client, user, another_user):
        """Успешная подписка создаёт запись в Subscription."""
        url = f'/api/users/{another_user.id}/subscribe/'
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
        assert Subscription.objects.filter(
            subscriber=user,
            author=another_user
        ).exists()

    def test_unsubscribe_success(self, auth_client, another_user):
        """Успешная отписка удаляет запись из Subscription."""
        url = f'/api/users/{another_user.id}/subscribe/'
        auth_client.post(url)
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
