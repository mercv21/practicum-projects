"""Сериализаторы для API (теги, ингредиенты, рецепты, подписки)."""

from django.contrib.auth import get_user_model
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag
)
from rest_framework import serializers

from .fields import Base64ImageField

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тега."""

    class Meta:
        """Мета-настройки сериализатора тегов."""

        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиента."""

    class Meta:
        """Мета-настройки сериализатора ингредиентов."""

        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для связующей модели ингредиента в рецепте (чтение)."""

    ingredient = IngredientSerializer(read_only=True)

    class Meta:
        """Мета-настройки сериализатора ингредиентов в рецепте."""

        model = IngredientInRecipe
        fields = ("id", "ingredient", "amount")


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя (чтение профиля)."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        """Мета-настройки сериализатора пользователя."""

        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar"
        )
        read_only_fields = ("id", "is_subscribed", "avatar")

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на данного автора."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            from recipes.models import Subscription
            return Subscription.objects.filter(
                subscriber=request.user,
                author=obj
            ).exists()
        return False


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели рецепта (только чтение)."""

    ingredients = IngredientInRecipeSerializer(
        many=True, read_only=True, source="ingredients_list"
    )
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Мета-настройки сериализатора рецептов (чтение)."""

        model = Recipe
        fields = (
            "id",
            "name",
            "text",
            "cooking_time",
            "image",
            "author",
            "tags",
            "ingredients",
            "pub_date",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_is_favorited(self, obj):
        """Рецепт добавлен в избранное текущим пользователем."""
        user = self.context["request"].user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Рецепт находится в корзине текущего пользователя."""
        user = self.context["request"].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецепта."""

    ingredients = serializers.ListField(
        child=serializers.DictField(), write_only=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField(write_only=True)

    class Meta:
        """Мета-настройки сериализатора создания/обновления рецепта."""

        model = Recipe
        fields = (
            "id",
            "name",
            "text",
            "cooking_time",
            "image",
            "tags",
            "ingredients",
        )

    def validate_tags(self, value):
        """Проверка на дубликаты тегов."""
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Теги не должны повторяться.")
        return value

    def validate_ingredients(self, value):
        """Проверка на дубликаты ингредиентов и наличие полей id/amount."""
        ids = [item.get("id") for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться."
            )

        existing_ids = set(Ingredient.objects.filter(
            id__in=ids
        ).values_list('id', flat=True))
        missing_ids = set(ids) - existing_ids
        if missing_ids:
            raise serializers.ValidationError(
                f"Ингредиенты с id {list(missing_ids)} не существуют."
            )

        for item in value:
            if "id" not in item or "amount" not in item:
                raise serializers.ValidationError(
                    "Каждый ингредиент должен содержать 'id' и 'amount'."
                )
            try:
                amount = int(item["amount"])
                if amount <= 0:
                    raise serializers.ValidationError(
                        "Количество ингредиента должно быть положительным."
                    )
            except (TypeError, ValueError):
                raise serializers.ValidationError(
                    "Количество ингредиента должно быть числом."
                )
        return value

    def create(self, validated_data):
        """Создаёт новый рецепт с тегами и ингредиентами."""
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        image = validated_data.pop("image")

        validated_data["author"] = self.context["request"].user

        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags)

        ingredient_objs = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient_id=item["id"],
                amount=item["amount"]
            )
            for item in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(ingredient_objs)

        if image:
            recipe.image = image
            recipe.save()

        return recipe

    def update(self, instance, validated_data):
        """Обновляет существующий рецепт."""
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)
        image = validated_data.pop("image", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags is not None:
            instance.tags.set(tags)

        if ingredients is not None:
            instance.ingredients_list.all().delete()
            ingredient_objs = [
                IngredientInRecipe(
                    recipe=instance,
                    ingredient_id=item["id"],
                    amount=item["amount"]
                )
                for item in ingredients
            ]
            IngredientInRecipe.objects.bulk_create(ingredient_objs)

        if image is not None:
            if instance.image:
                instance.image.delete(save=False)
            instance.image = image
            instance.save()

        return instance


class SubscriptionSerializer(UserSerializer):
    """Сериализатор для подписок (расширяет UserSerializer рецептами)."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        """Мета-настройки сериализатора подписок."""

        fields = (
            *UserSerializer.Meta.fields,
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        """Возвращает рецепты автора с учётом фильтрации по тегам и лимита."""
        request = self.context["request"]
        limit = request.query_params.get("recipes_limit")
        tags_param = request.query_params.get("tags")
        recipes = obj.recipes.all()
        if tags_param:
            tag_slugs = [
                slug.strip() for slug in tags_param.split(",") if slug.strip()
            ]
            if tag_slugs:
                recipes = recipes.filter(tags__slug__in=tag_slugs)
        if limit:
            try:
                limit_int = int(limit)
                recipes = recipes[:limit_int]
            except ValueError:
                pass
        return RecipeSerializer(recipes, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        """Возвращает общее количество рецептов автора."""
        return obj.recipes.count()
