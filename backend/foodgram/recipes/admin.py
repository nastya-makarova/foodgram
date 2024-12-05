from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShortLinkRecipe,
    TagRecipe,
    Tag
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_editable = ('name', 'slug')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'get_favorite_count')
    list_editable = ('author', 'name',)
    search_fields = ('author', 'name')
    list_filter = ('tags',)

    def get_favorite_count(self, obj):
        """Метод считает количество добавлений рецепта в избранное."""
        return Favorite.objects.filter(recipe=obj).count()




@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'recipe')
    list_display_links = ('recipe', 'tag')


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'ingredient', 'recipe', 'amount')
    list_display_links = ('ingredient', 'recipe')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')


@admin.register(ShortLinkRecipe)
class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'short_link')
