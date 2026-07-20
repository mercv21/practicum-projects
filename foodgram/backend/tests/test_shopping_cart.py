"""Тесты для API списка покупок."""

import pytest
from django.urls import reverse
from recipes.models import ShoppingCart
from rest_framework import status


@pytest.mark.django_db
class TestShoppingCartAPI:
    """Добавления/удаления рецептов из корзины, скачивания списка."""

    def test_add_to_cart(self, auth_client, user, recipe):
        """Добавление рецепта в корзину возвращает 201."""
        url = reverse('recipe-shopping-cart', args=[recipe.id])
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
        assert ShoppingCart.objects.filter(user=user, recipe=recipe).exists()

    def test_add_twice(self, auth_client, recipe):
        """Повторное добавление того же рецепта возвращает 400."""
        url = reverse('recipe-shopping-cart', args=[recipe.id])
        response1 = auth_client.post(url)
        assert response1.status_code == status.HTTP_201_CREATED
        response2 = auth_client.post(url)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_remove_from_cart(self, auth_client, recipe):
        """Удаление рецепта из корзины возвращает 204."""
        url = reverse('recipe-shopping-cart', args=[recipe.id])
        auth_client.post(url)
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_download_shopping_cart(self, auth_client, recipe, ingredient):
        """Скачивание списка покупок возвращает файл с ингредиентами."""
        add_url = reverse('recipe-shopping-cart', args=[recipe.id])
        auth_client.post(add_url)

        url = reverse('recipe-download-shopping-cart')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/plain'
        assert response[
            'Content-Disposition'
        ] == 'attachment; filename="shopping_list.txt"'
        content = response.content.decode()
        assert ingredient.name in content
        assert '100' in content
