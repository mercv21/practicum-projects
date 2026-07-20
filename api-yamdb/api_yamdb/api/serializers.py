from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers

from .validators import (
    validate_username_chars,
    validate_username_lenght,
    validate_username_not_me
)
from reviews.constants import (
    EMAIL_FIELD_LIMIT,
    MAX_SCORE_REVIEW,
    MIN_SCORE_REVIEW,
    USERNAME_FIELD_LIMIT
)
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            validate_username_not_me,
            validate_username_lenght,
            validate_username_chars
        ]
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and not (
            request.user.is_admin or request.user.is_superuser
        ):
            validated_data.pop('role', None)
        return super().update(instance, validated_data)

    def validate(self, data):
        if self.instance is None:
            username = data.get('username')
            if username and User.objects.filter(
                username=username
            ).exists():
                raise serializers.ValidationError(
                    {'username': 'Пользователь с таким username уже есть'}
                )

            email = data.get('email')
            if email and User.objects.filter(email=email).exists():
                raise serializers.ValidationError(
                    {'email': 'Пользователь с таким email уже существует'}
                )
        return data


class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=USERNAME_FIELD_LIMIT,
        validators=[
            validate_username_not_me,
            validate_username_lenght,
            validate_username_chars
        ]
    )
    email = serializers.EmailField(max_length=EMAIL_FIELD_LIMIT)

    def validate(self, data):
        """Проверка: username не занят другим email и наоборот."""
        username = data.get('username')
        email = data.get('email')

        if User.objects.filter(
            username=username
        ).exclude(email=email).exists():
            raise serializers.ValidationError(
                {'username': 'Это имя уже занято.'}
            )
        if User.objects.filter(
            email=email
        ).exclude(username=username).exists():
            raise serializers.ValidationError(
                {'email': 'Этот email уже занят.'}
            )
        return data

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        return user


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Для чтения — вложенные объекты genre и category."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(
        read_only=True,
        default=0
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    """Для записи — принимает slug, возвращает вложенные объекты."""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        required=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    year = serializers.IntegerField(
        required=True
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category'
        )

    def validate_year(self, value):
        """Проверяем, что год не из будущего."""
        if value > timezone.now().year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего!'
            )
        return value

    def to_representation(self, instance):
        return TitleReadSerializer(instance).data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    message = f'Оценка должна быть от {MIN_SCORE_REVIEW} до {MAX_SCORE_REVIEW}'

    score = serializers.IntegerField(
        min_value=MIN_SCORE_REVIEW,
        max_value=MAX_SCORE_REVIEW,
        error_messages={
            'min_value': message,
            'max_value': message,
        }
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        """Проверяем, что пользователь не оставил повторный отзыв."""
        request = self.context.get('request')

        if request.method == 'POST':
            title_id = self.context.get('view').kwargs.get('title_id')
            author = request.user
            if Review.objects.filter(
                title_id=title_id,
                author=author
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError('Неверный код подтверждения')

        data['user'] = user
        return data
