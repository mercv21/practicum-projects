"""Тесты для API пользователей."""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestUserAPI:
    """Тестирование регистрации, токена, профиля, аватара."""

    def test_registration_duplicate_email(self, api_client, user):
        """Регистрация с уже существующим email возвращает 400."""
        url = reverse('user-list')
        data = {
            'email': user.email,
            'username': 'another',
            'first_name': 'Test',
            'last_name': 'Test',
            'password': 'pass123',
            're_password': 'pass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_token_login_invalid(self, api_client, user):
        """Вход с неверным паролем возвращает 400."""
        url = '/api/auth/token/login/'
        data = {'email': user.email, 'password': 'wrong'}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_me_unauthorized(self, api_client):
        """Запрос без токена возвращает 401."""
        url = reverse('user-me')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_me_authorized(self, auth_client, user):
        """Авторизованный запрос возвращает данные пользователя."""
        url = reverse('user-me')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == user.id
        assert 'is_subscribed' in response.data

    def test_avatar_upload(self, auth_client, user, image_base64):
        """Загрузка аватара возвращает URL и сохраняет аватар."""
        url = reverse('avatar')
        base64_image = image_base64
        response = auth_client.put(
            url,
            {'avatar': base64_image},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'avatar' in response.data
        user.refresh_from_db()
        assert user.avatar is not None

    def test_avatar_delete(self, auth_client, user, image_base64):
        """Удаление аватара возвращает 204 и очищает поле avatar."""
        url = reverse('avatar')
        base64_image = image_base64
        auth_client.put(url, {'avatar': base64_image}, format='json')
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert not user.avatar
