"""API: теги, ингредиенты, рецепты, пользователи, подписки, аватар."""

import base64
import secrets
import string

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    ShortLink,
    Subscription,
    Tag
)
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.utils import generate_shopping_list_text

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserSerializer
)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов (только чтение)."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов (только чтение) с фильтрацией по имени."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    ]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    queryset = Recipe.objects.all().order_by('-pub_date')

    def get_serializer_class(self):
        """Возвращает соответствующий сериализатор."""
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        return RecipeCreateUpdateSerializer

    @staticmethod
    def generate_short_id(length=6):
        """Генерирует случайный уникальный короткий идентификатор."""
        alphabet = string.ascii_letters + string.digits
        while True:
            short_id = ''.join(secrets.choice(alphabet) for _ in range(length))
            if not ShortLink.objects.filter(short_id=short_id).exists():
                return short_id

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт."""
        recipe = self.get_object()
        short_link, created = ShortLink.objects.get_or_create(
            recipe=recipe,
            defaults={'short_id': self.generate_short_id()}
        )
        full_url = request.build_absolute_uri(f'/s/{short_link.short_id}')
        return Response({'short-link': full_url})

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        """Добавляет или удаляет рецепт из избранного."""
        recipe = self.get_object()
        if request.method == 'POST':
            if Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'detail': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            deleted, _ = Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'detail': 'Рецепта нет в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        """Добавляет или удаляет рецепт из списка покупок."""
        recipe = self.get_object()
        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'detail': 'Рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            deleted, _ = ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'detail': 'Рецепта нет в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачивает текстовый файл со списком покупок."""
        file_content = generate_shopping_list_text(request.user)
        response = HttpResponse(file_content, content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_list.txt"'
        return response


class UserViewSet(viewsets.GenericViewSet):
    """Вьюсет для пользователей: просмотр профиля, подписки, отписка."""

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        """Возвращает публичную информацию о пользователе."""
        user = self.get_object()
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        """Возвращает список авторов, на которых подписан пользователь."""
        user = request.user
        subscriptions = Subscription.objects.filter(
            subscriber=user
        ).select_related('author')
        authors = [sub.author for sub in subscriptions]
        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = SubscriptionSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            authors,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        """Подписаться или отписаться от автора."""
        author = self.get_object()
        user = request.user
        if request.method == 'POST':
            if user == author:
                return Response(
                    {'detail': 'Нельзя подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscription.objects.filter(
                subscriber=user,
                author=author
            ).exists():
                return Response(
                    {'detail': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(subscriber=user, author=author)
            serializer = SubscriptionSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            deleted, _ = Subscription.objects.filter(
                subscriber=user,
                author=author
            ).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'detail': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class AvatarView(APIView):
    """Представление для загрузки и удаления аватара текущего пользователя."""

    permission_classes = [IsAuthenticated]

    def put(self, request):
        """Обновляет аватар пользователя."""
        avatar_base64 = request.data.get('avatar')
        if not avatar_base64:
            return Response({'detail': 'Поле "avatar" обязательно.'},
                            status=status.HTTP_400_BAD_REQUEST)
        ext = 'png'
        if 'data:image/' in avatar_base64:
            try:
                mime_part = avatar_base64.split(';')[0]
                ext = mime_part.split('/')[-1]
            except IndexError:
                pass
        if ',' in avatar_base64:
            avatar_base64 = avatar_base64.split(',')[1]
        try:
            image_data = base64.b64decode(avatar_base64)
        except Exception as e:
            return Response({'detail': f'Неверный формат base64: {str(e)}'},
                            status=status.HTTP_400_BAD_REQUEST)
        file_name = f'avatar_{request.user.id}.{ext}'
        request.user.avatar.save(file_name, ContentFile(image_data), save=True)
        return Response({'avatar': request.build_absolute_uri(
            request.user.avatar.url
        )}, status=status.HTTP_200_OK)

    def delete(self, request):
        """Удаляет аватар текущего пользователя."""
        if request.user.avatar:
            request.user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
