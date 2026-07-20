"""Маршруты API приложения."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AvatarView,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet
)

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('users', UserViewSet, basename='user')

urlpatterns = router.urls
urlpatterns += [
    path('users/me/avatar/', AvatarView.as_view(), name='avatar'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
