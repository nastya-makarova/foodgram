from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShortLinkRecipe,
    Tag,
    ShoppingList
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_editable = ('name', 'slug')


class IngredientRecipeAdmin(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_author_link', 'get_favorite_count')
    list_editable = ('name',)
    search_fields = ('author__username', 'name')
    list_filter = ('tags',)
    inlines = (IngredientRecipeAdmin,)

    def get_favorite_count(self, obj):
        """Метод считает количество добавлений рецепта в избранное."""
        return Favorite.objects.filter(recipe=obj).count()

    def get_author_link(self, obj):
        """
        Метод для отображения имени автора как ссылки.
        При клике на имя открывается страница редактирования пользователя.
        """
        if obj.author:
            return format_html(
                '<a href="/admin/users/foodgramuser/{}/change/">{}</a>',
                obj.author.id, obj.author.username
            )
        return "-"

    get_author_link.short_description = 'Автор'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(ShortLinkRecipe)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'short_link')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'current_user')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'current_user')
