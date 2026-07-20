from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .constants import TEXT_LIMIT_ADMIN
from .models import Category, Comment, Genre, Review, Title, User


@admin.register(User)
class UserWithRoleAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'bio')
    list_filter = ('role',)
    search_fields = ('username', 'email')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom Fields', {'fields': ('role', 'bio', 'confirmation_code')}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):

    list_display = ('name', 'year', 'category', 'genre_list')
    list_filter = ('year', 'category')
    filter_horizontal = ('genre',)

    @admin.display(description='Жанры',)
    def genre_list(self, obj):
        return ', '.join([g.name for g in obj.genre.all()])


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'score', 'pub_date', 'short_review')
    list_filter = ('score', 'pub_date')

    @admin.display(description='Отзыв',)
    def short_review(self, obj):
        if len(obj.text) > TEXT_LIMIT_ADMIN:
            return obj.text[:TEXT_LIMIT_ADMIN] + '...'
        return obj.text


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('review', 'author', 'pub_date', 'short_comment')

    @admin.display(description='Комментарий',)
    def short_comment(self, obj):
        if len(obj.text) > TEXT_LIMIT_ADMIN:
            return obj.text[:TEXT_LIMIT_ADMIN] + '...'
        return obj.text
