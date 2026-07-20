from django.contrib.auth.models import AbstractUser
from django.db import models

from api.validators import (
    validate_username_chars,
    validate_username_not_me,
    validate_year
)
from reviews.constants import (
    EMAIL_FIELD_LIMIT,
    NAME_FIELD_LIMIT,
    ROLE_FIELD_LIMIT,
    SYMBOL_LIMIT,
    USERNAME_FIELD_LIMIT
)


class CategoryGenreBaseModel(models.Model):
    """Абстрактная модель с полями name и slug."""

    name = models.CharField(
        verbose_name='Название жанра',
        max_length=NAME_FIELD_LIMIT
    )
    slug = models.SlugField(
        unique=True
    )

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name[:SYMBOL_LIMIT]


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    ]

    username = models.CharField(
        max_length=USERNAME_FIELD_LIMIT,
        unique=True,
        validators=[validate_username_not_me, validate_username_chars],
    )
    email = models.EmailField(
        'email address',
        max_length=EMAIL_FIELD_LIMIT,
        unique=True,
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль',
        max_length=ROLE_FIELD_LIMIT,
        choices=ROLE_CHOICES,
        default=USER,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR


class ReviewCommentBaseModel(models.Model):
    """Абстрактная модель с полем pub_date."""

    text = models.TextField(
        verbose_name='Текст'
    )

    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    class Meta:
        abstract = True
        ordering = ['-pub_date']
        default_related_name = '%(app_label)s_%(class)s_related'

    def __str__(self):
        return self.text[:SYMBOL_LIMIT]


class Genre(CategoryGenreBaseModel):
    """Жанр произведения."""

    class Meta(CategoryGenreBaseModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Category(CategoryGenreBaseModel):
    """Категория произведения."""

    class Meta(CategoryGenreBaseModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    """Произведение."""

    name = models.CharField(
        verbose_name='Название произведения',
        max_length=NAME_FIELD_LIMIT
    )
    year = models.SmallIntegerField(
        verbose_name='Год релиза',
        validators=[validate_year]
    )

    description = models.TextField(
        verbose_name='Описание',
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанры',
        related_name='titles'
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:SYMBOL_LIMIT]


class Review(ReviewCommentBaseModel):
    """Отзыв на произведение."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    score = models.IntegerField(
        verbose_name='Оценка'
    )

    class Meta(ReviewCommentBaseModel.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]


class Comment(ReviewCommentBaseModel):
    """Комментарий к отзыву."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta(ReviewCommentBaseModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
