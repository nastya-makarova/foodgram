from rest_framework import serializers

from recipes.models import Recipe


class RecipeSerializeer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )