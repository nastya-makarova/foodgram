import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (Favorite,
                            Ingredient,
                            IngredientRecipe,
                            Recipe,
                            ShoppingList,
                            Tag,
                            TagRecipe,
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
    """Сериализатор для модели IngredientRecipe при отображении рецепта."""
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
    author = UserSerializer()
    ingredients = IngredientRecipeSerializer(
        source='ingredientrecipe', many=True
    )
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
        if obj.author:
            current_user = obj.author
        else:
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
        if obj.author:
            current_user = obj.author
        else:
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

    def to_representation(self, instance):
        """Метод изменяет формат вывода данных для ингредиентов."""
        representation = super().to_representation(instance)
        ingredients_data = representation.pop('ingredients')
        ingredients = []
        for ingredient in ingredients_data:
            ingredients.append({
                'id': ingredient['ingredient']['id'],
                'name': ingredient['ingredient']['name'],
                'measurement_unit': ingredient['ingredient']['measurement_unit'],
                'amount': ingredient['amount']}
            )
        representation['ingredients'] = ingredients
        return representation


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания или изменения объекта Recipe."""
    ingredients = IngredientRecipeCreateSerializer(
        source='ingredient', many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'cooking_time')

    def validate_cooking_time(self, value):
        """Метод проверяет, значение времени готовки.
        Оно должно быть не менее 1 мин.
        """
        if value <= 0:
            raise serializers.ValidationError(
                'Значение времни приготовления должно быть не менее 1 мин.'
            )
        return value

    def to_internal_value(self, data):
        """
        Метод преобразует входные данные для ингредиентов при создании рецепта.
        Преобразованные данные, где поле 'ingredients' будет списком словарей
        с ключами 'id' и 'amount'.
        """
        if 'ingredients' in data:
            ingredients = []
            for ingredient in data['ingredients']:
                ingredients.append(
                    {
                        'id': ingredient['id'],
                        'amount': ingredient['amount']
                    }
                )
            data['ingredients'] = ingredients
        return data

    def create(self, validated_data):
        """Переопределят метод для создания объекта модели Recipe.
        и создает соответствующие записи в связанных таблицах
        (для Tag и Ingredient).
        """
        author = self.context['request'].user
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(author=author, **validated_data)
        for tag in tags_data:
            tag = Tag.objects.get(id=tag)
            TagRecipe.objects.create(recipe=recipe, tag=tag)
        for ingredient in ingredients_data:
            amount = ingredient['amount']
            ingredient = Ingredient.objects.get(id=ingredient['id'])
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)

        if 'tags' not in validated_data:
            instance.save()
        else:
            tags_data = validated_data.pop('tags')
            for tag in tags_data:
                tag = Tag.objects.get(id=tag)
                TagRecipe.objects.create(recipe=instance, tag=tag)

        if 'ingredients' not in validated_data:
            instance.save()
        else:
            ingredients_data = validated_data.pop('ingredients')
            for ingredient in ingredients_data:
                amount = ingredient['amount']
                ingredient = Ingredient.objects.get(id=ingredient['id'])
                IngredientRecipe.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=amount
                )

        instance.save()
        return instance

    def to_representation(self, recipe):
        """Метод изменяет сериализатор для отображение объекта Recipe.
        Используется при формировании ответа на POST или PATCH запрос."""
        serializer = RecipeSerializer(recipe)
        return serializer.data


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
