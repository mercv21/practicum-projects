"""Фикстуры для тестов."""
from decimal import Decimal

import pytest
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag
)
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import User
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.fixture
def image_base64():
    """Возвращает base64-строку PNG изображения 1x1 пиксель."""
    return (
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAE"
        "AAAABAgMAAABieywaAAAACVBMVEUAAAD"
        "///9fX1/S0ecCAAAACXBIWXMAAA7EAAA"
        "OxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAA"
        "BJRU5ErkJggg=="
    )


@pytest.fixture
def image_file():
    """Создаёт тестовый файл изображения."""
    return SimpleUploadedFile(
        'test_image.jpg',
        b'fake_image_content',
        content_type='image/jpeg'
    )


@pytest.fixture
def api_client():
    """Возвращает неаутентифицированный APIClient."""
    return APIClient()


@pytest.fixture
def user(db):
    """Возвращает обычного пользователя."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def another_user(db):
    """Возвращает второго пользователя."""
    return User.objects.create_user(
        username="another",
        email="another@example.com",
        password="testpass123",
        first_name="Another",
        last_name="User",
    )


@pytest.fixture
def auth_client(user):
    """Возвращает APIClient с токеном аутентификации пользователя."""
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.fixture
def tag(db):
    """Возвращает тег 'Завтрак'."""
    return Tag.objects.create(
        name="Завтрак",
        slug="breakfast",
    )


@pytest.fixture
def ingredient(db):
    """Возвращает ингредиент 'Сахар' в граммах."""
    return Ingredient.objects.create(
        name="Сахар",
        measurement_unit="г",
    )


@pytest.fixture
def recipe(db, user, tag, ingredient, image_file):
    """Возвращает рецепт, связанный с пользователем, тегом и ингредиентом."""
    recipe = Recipe.objects.create(
        author=user,
        name="Тестовый рецепт",
        text="Описание",
        cooking_time=30,
        image=image_file,
    )
    recipe.tags.set([tag])
    IngredientInRecipe.objects.create(
        recipe=recipe,
        ingredient=ingredient,
        amount=Decimal("100.00"),
    )
    return recipe


@pytest.fixture
def favorite(db, user, recipe):
    """Возвращает запись избранного для пользователя и рецепта."""
    return Favorite.objects.create(
        user=user,
        recipe=recipe,
    )


@pytest.fixture
def shopping_cart(db, user, recipe):
    """Возвращает запись корзины покупок для пользователя и рецепта."""
    return ShoppingCart.objects.create(
        user=user,
        recipe=recipe,
    )


@pytest.fixture
def subscription(db, user, another_user):
    """Возвращает подписку пользователя на другого пользователя."""
    return Subscription.objects.create(
        subscriber=user,
        author=another_user,
    )
