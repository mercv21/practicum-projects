"""Тесты для API рецептов."""

import pytest
from django.urls import reverse
from recipes.models import Favorite, Recipe
from rest_framework import status


@pytest.mark.django_db
class TestRecipeAPI:
    """Тесты для эндпоинтов рецептов."""

    def test_list_recipes(self, api_client, recipe):
        """Получение списка рецептов."""
        url = reverse('recipe-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert len(response.data['results']) == 1

    def test_create_recipe_unauthorized(
            self,
            api_client,
            tag,
            ingredient,
            image_base64
    ):
        """Неавторизованный пользователь не может создать рецепт."""
        url = reverse('recipe-list')
        data = {
            'name': 'Новый рецепт',
            'text': 'Описание',
            'cooking_time': 15,
            'image': image_base64,
            'tags': [tag.id],
            'ingredients': [{'id': ingredient.id, 'amount': 50}]
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_recipe_success(
            self,
            auth_client,
            user,
            tag,
            ingredient,
            image_base64
    ):
        """Авторизованный пользователь может создать рецепт."""
        url = reverse('recipe-list')
        data = {
            'name': 'Мой рецепт',
            'text': 'Приготовление',
            'cooking_time': 20,
            'image': image_base64,
            'tags': [tag.id],
            'ingredients': [{'id': ingredient.id, 'amount': 100}]
        }
        response = auth_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Recipe.objects.filter(name='Мой рецепт', author=user).exists()

    def test_retrieve_recipe(self, api_client, recipe):
        """Получение одного рецепта по id."""
        url = reverse('recipe-detail', args=[recipe.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == recipe.id
        assert 'is_favorited' in response.data

    def test_update_recipe_owner(self, auth_client, recipe):
        """Владелец может редактировать свой рецепт."""
        url = reverse('recipe-detail', args=[recipe.id])
        data = {'name': 'Обновлённое название'}
        response = auth_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        recipe.refresh_from_db()
        assert recipe.name == 'Обновлённое название'

    def test_update_recipe_not_owner(self, auth_client, another_user, recipe):
        """Не владелец не может редактировать чужой рецепт."""
        auth_client.force_authenticate(user=another_user)
        url = reverse('recipe-detail', args=[recipe.id])
        data = {'name': 'Чужое обновление'}
        response = auth_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_recipe_owner(self, auth_client, user, recipe):
        """Владелец может удалить свой рецепт."""
        url = reverse('recipe-detail', args=[recipe.id])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Recipe.objects.filter(id=recipe.id).exists()

    def test_filter_by_tags(self, api_client, tag, recipe):
        """Фильтрация рецептов по тегам."""
        url = reverse('recipe-list') + f'?tags={tag.slug}'
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_filter_by_author(self, api_client, user, recipe):
        """Фильтрация рецептов по автору."""
        url = reverse('recipe-list') + f'?author={user.id}'
        response = api_client.get(url)
        assert response.data['count'] == 1

    def test_favorite_action(self, auth_client, user, recipe):
        """Добавление/удаление рецепта в избранное."""
        url = reverse('recipe-favorite', args=[recipe.id])
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
        assert Favorite.objects.filter(user=user, recipe=recipe).exists()
        response2 = auth_client.post(url)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        response3 = auth_client.delete(url)
        assert response3.status_code == status.HTTP_204_NO_CONTENT
        assert not Favorite.objects.filter(user=user, recipe=recipe).exists()

    def test_is_favorited_field(self, auth_client, recipe, favorite):
        """Поле is_favorited присутствует и корректно."""
        url = reverse('recipe-list')
        response = auth_client.get(url)
        assert response.data['results'][0]['is_favorited'] is True

    def test_short_link(self, auth_client, recipe):
        """Получение короткой ссылки на рецепт."""
        url = reverse('recipe-get-link', args=[recipe.id])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'short-link' in response.data
        response2 = auth_client.get(url)
        assert response2.data['short-link'] == response.data['short-link']
