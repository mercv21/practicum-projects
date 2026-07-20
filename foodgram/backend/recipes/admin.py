"""Регистрация моделей рецептов в административной панели."""

from django.contrib import admin
from django.db.models import Count

from .models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    ShortLink,
    Subscription,
    Tag,
)

MIN_NUM_INGREDIENT_IN_LINE = 1
EXTRA_NUM_INGREDIENT_IN_LINE = 0


class IngredientInline(admin.TabularInline):
    """Inline для ингредиентов в рецепте."""

    model = IngredientInRecipe
    extra = EXTRA_NUM_INGREDIENT_IN_LINE
    min_num = MIN_NUM_INGREDIENT_IN_LINE
    fields = ('ingredient', 'amount')
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройка отображения рецепта в админке."""

    list_display = ("id", "name", "author", "pub_date", "favorite_count")
    search_fields = ("name", "author__username")
    list_filter = ("tags", "author")
    readonly_fields = ("favorite_count",)
    inlines = [IngredientInline]

    @admin.display(description='В избранном')
    def favorite_count(self, obj):
        """Возвращает количество добавлений рецепта в избранное."""
        return obj.favorited_by.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройка отображения ингредиента в админке."""

    list_display = ("name", "measurement_unit", "recipes_count")
    search_fields = ("name", "measurement_unit")
    list_filter = ("measurement_unit",)

    def get_queryset(self, request):
        """Аннотирует каждый ингредиент количеством рецептов."""
        return super().get_queryset(request).annotate(
            recipes_count=Count('ingredientinrecipe')
        )

    @admin.display(description='В рецептах')
    def recipes_count(self, obj):
        """Возвращает количество рецептов, содержащих данный ингредиент."""
        return obj.recipes_count


admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(Subscription)
admin.site.register(ShortLink)
admin.site.register(IngredientInRecipe)
