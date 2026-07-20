from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitleFilter
from .permissions import (
    IsAdmin,
    IsAdminOrModeratorOrReadOnly,
    IsAdminOrReadOnly
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    TokenSerializer,
    UserCreateSerializer,
    UserSerializer
)
from reviews.models import Category, Genre, Review, Title


User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """Регистрация нового пользователя."""
    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    confirmation_code = default_token_generator.make_token(user)

    send_mail(
        'Код подтверждения для YaMDb',
        f'Ваш код подтверждения: {confirmation_code}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def token(request):
    """Получение JWT токена."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.validated_data['user']

    token = AccessToken.for_user(user)
    return Response({'token': str(token)}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Управление пользователями."""

    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [IsAdmin]
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']

    @action(
        detail=False,
        methods=['get', 'patch',],
        url_path='me',
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Свой профиль."""

        user = request.user

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data)


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Базовый ViewSet:

    -создание,
    -список,
    -удаление.
    """

    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    """ViewSet для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CreateListDestroyViewSet):
    """ViewSet для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для произведений."""

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [
        filters.OrderingFilter,
        DjangoFilterBackend
    ]
    filterset_class = TitleFilter

    def get_queryset(self):
        return Title.objects.annotate(
            rating=Avg('reviews__score')
        ).order_by('name')

    def get_serializer_class(self):
        if self.action in permissions.SAFE_METHODS:
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов."""

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAdminOrModeratorOrReadOnly
    ]

    def get_title(self):
        """Метод для получения произведения."""
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def get_queryset(self):
        """Метод для получения всех отзывы к произведению."""
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        """Метод для создания новыго отзыва."""
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев."""

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAdminOrModeratorOrReadOnly
    ]

    def get_review(self):
        """Получение отзыва по ID с проверкой принадлежности произведению."""
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(
            Review,
            id=review_id,
            title_id=title_id
        )

    def get_queryset(self):
        """Получение всех комментариев для конкретного отзыва."""
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        """Создание нового комментария."""
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
