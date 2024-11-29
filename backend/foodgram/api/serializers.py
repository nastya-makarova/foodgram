import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (Favorite,
                            Ingredient,
                            IngredientRecipe,
                            Recipe,
                            ShoppingList,
                            Tag,
                            User)


class Base64ImageField(serializers.ImageField):
    """Поле для обработки изображений в формате base64 в сериализаторе."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели IngredientRecipe."""
    ingredient = IngredientSerializer()

    class Meta:
        model = IngredientRecipe
        fields = ('ingredient', 'amount')

    def validate_amount(self, value):
        """Метод проверяет, что введеное количество ингредиента больше 0."""
        if value <= 0:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше нуля.'
            )
        return value


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""
    tags = TagSerializer(many=True)
    author = UserSerializer
    ingredients = IngredientRecipeSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        read_only_fields = ('author', 'image')

    def get_is_favorite(self, obj):
        """
        Метод проверяет, есть ли рецепт в избранном
        у текущего пользователя.
        """
        current_user = self.context['request'].user
        if current_user.is_authenticated:
            return Favorite.objects.filter(
                current_user=current_user,
                recipe=obj
            ).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        Метод проверяет, есть ли рецепт в списке покупок
        у текущего пользователя.
        """
        current_user = self.context['request'].user
        if current_user.is_authenticated:
            return ShoppingList.objects.filter(
                current_user=current_user,
                recipe=obj
            ).exists()

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None