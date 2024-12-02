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
    ingredient = IngredientSerializer(read_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('ingredient', 'amount')


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для модели IngredientRecipe при создании рецепта."""
    ingredient = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

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
    """Сериализатор для отображения объекта модели Recipe."""
    tags = TagSerializer(many=True)
    author = UserSerializer
    ingredients = IngredientRecipeSerializer(many=True)
    is_favorite = serializers.SerializerMethodField(default=False)
    is_in_shopping_cart = serializers.SerializerMethodField(default=False)
    image = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorite',
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
        """Метод получает URL изображения."""
        if obj.image:
            return obj.image.url
        return None


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'cooking_time')


class RecipeResponseSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image_url(self, obj):
        """Метод получает URL изображения."""
        if obj.image:
            return obj.image.url
        return None