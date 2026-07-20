"""Фильтры для API (ингредиенты, рецепты)."""

from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    """Фильтр для ингредиентов: поиск по началу названия без учёта регистра."""

    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        """Мета-настройки фильтра ингредиентов."""

        model = Ingredient
        fields = ['name']


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов."""

    author = filters.NumberFilter(field_name='author__id')
    tags = filters.BaseInFilter(field_name='tags__slug', lookup_expr='in')
    is_favorited = filters.BooleanFilter(method='filter_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_in_shopping_cart'
    )

    def filter_favorited(self, queryset, name, value):
        """Возвращает рецепты, добавленные в избранное."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorited_by__user=self.request.user)
        return queryset

    def filter_in_shopping_cart(self, queryset, name, value):
        """Возвращает рецепты, добавленные в список покупок."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(in_shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        """Мета-настройки фильтра рецептов."""

        model = Recipe
        fields = ['author', 'tags']
