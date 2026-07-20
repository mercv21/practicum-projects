"""Модели для приложения рецептов."""
import secrets
import string

from django.core.validators import MinValueValidator
from django.db import models

MAX_LEN_NAME = 256
MAX_LEN_SLUG = 64
MAX_LEN_UNIT = 64
MIN_COOKING_TIME = 1
MAX_AMOUNT_DIGITS = 10
AMOUNT_DECIMAL_PLACES = 2
MIN_AMOUNT = 1
MAX_LEN_SHORT_ID = 10


class BaseUserRecipeRelation(models.Model):
    """Абстрактная базовая модель для связи пользователь-рецепт."""

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)

    class Meta:
        """Мета-настройки абстрактной модели."""

        abstract = True
        unique_together = ('user', 'recipe')


class Tag(models.Model):
    """Модель тега для рецептов."""

    name = models.CharField(max_length=MAX_LEN_NAME, unique=True)
    slug = models.SlugField(max_length=MAX_LEN_SLUG, unique=True)

    class Meta:
        """Мета-настройки модели тега."""

        ordering = ('name',)

    def __str__(self):
        """Возвращает строковое представление тега."""
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента с единицей измерения."""

    name = models.CharField(max_length=MAX_LEN_NAME)
    measurement_unit = models.CharField(
        max_length=MAX_LEN_UNIT,
        help_text="например, 'г', 'кг', 'ст. ложка'"
    )

    class Meta:
        """Мета-настройки модели ингредиента."""

        unique_together = ('name', 'measurement_unit')
        ordering = ('name',)

    def __str__(self):
        """Возвращает строковое представление ингредиента."""
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(max_length=MAX_LEN_NAME)
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_COOKING_TIME)]
    )
    image = models.ImageField(upload_to='recipes/images/')
    tags = models.ManyToManyField('Tag', related_name='recipes')
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Мета-настройки модели рецепта."""

        ordering = ('-pub_date',)

    def __str__(self):
        """Возвращает название рецепта."""
        return self.name


class IngredientInRecipe(models.Model):
    """Связующая модель для ингредиентов в рецепте с количеством."""

    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='ingredients_list'
    )
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=MAX_AMOUNT_DIGITS,
        decimal_places=AMOUNT_DECIMAL_PLACES,
        validators=[MinValueValidator(MIN_AMOUNT)]
    )

    class Meta:
        """Мета-настройки связующей модели."""

        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        """Возвращает строковое представление ингредиента с количеством."""
        return f"{self.ingredient} - {self.amount}"


class Favorite(BaseUserRecipeRelation):
    """Модель избранного: связь пользователь-рецепт."""

    class Meta(BaseUserRecipeRelation.Meta):
        """Мета-настройки модели избранного."""

        abstract = False
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        """Возвращает строковое представление избранного."""
        return f"{self.user} добавил {self.recipe} в избранное"


class ShoppingCart(BaseUserRecipeRelation):
    """Модель корзины покупок: связь пользователь-рецепт."""

    class Meta(BaseUserRecipeRelation.Meta):
        """Мета-настройки модели корзины."""

        abstract = False
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'

    def __str__(self):
        """Возвращает строковое представление корзины."""
        return f"{self.user} добавил {self.recipe} в корзину"


class Subscription(models.Model):
    """Модель подписки: пользователь подписывается на автора."""

    subscriber = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        """Мета-настройки модели подписки."""

        unique_together = ('subscriber', 'author')
        ordering = ('-id',)

    def __str__(self):
        """Возвращает строковое представление подписки."""
        return f"{self.subscriber} подписан на {self.author}"


class ShortLink(models.Model):
    """Модель короткой ссылки для рецепта."""

    recipe = models.OneToOneField(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='short_link',
    )
    short_id = models.CharField(
        unique=True,
        max_length=MAX_LEN_SHORT_ID,
        blank=False,
        editable=False,
    )

    def save(self, *args, **kwargs):
        """Генерирует уникальный short_id перед сохранением."""
        if not self.short_id:
            self.short_id = self.generate_unique_short_id()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_short_id(length=6):
        """Генерирует случайный уникальный short_id заданной длины."""
        alphabet = string.ascii_letters + string.digits
        while True:
            short_id = ''.join(secrets.choice(alphabet) for _ in range(length))
            if not ShortLink.objects.filter(short_id=short_id).exists():
                return short_id

    def __str__(self):
        """Возвращает короткий идентификатор ссылки."""
        return self.short_id
