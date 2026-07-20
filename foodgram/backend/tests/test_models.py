"""Тесты для моделей."""

import pytest
from django.core.exceptions import ValidationError
from recipes.models import Recipe


@pytest.mark.django_db
class TestModels:
    """Тесты моделей приложения."""

    def test_user_creation(self, user):
        """Создание пользователя и его строковоге представления."""
        assert user.email == 'test@example.com'
        assert str(user) == 'testuser'

    def test_tag_str(self, tag):
        """Строкового представления тега."""
        assert str(tag) == 'Завтрак'

    def test_ingredient_str(self, ingredient):
        """Строкового представления ингредиента."""
        assert str(ingredient) == 'Сахар (г)'

    def test_recipe_cooking_time_validation(self, user):
        """Время приготовления не может быть 0."""
        with pytest.raises(ValidationError):
            recipe = Recipe(
                author=user,
                name='Test',
                text='Text',
                cooking_time=0
            )
            recipe.full_clean()
