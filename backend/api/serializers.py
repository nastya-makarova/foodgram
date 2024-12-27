import base64
import re

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingList,
    ShortLinkRecipe,
    Tag,
    User,
)
from users.models import Subscription


class Base64ImageField(serializers.ImageField):
    """Поле для обработки изображений в формате base64 в сериализаторе."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения объекта модели User."""
    avatar = serializers.SerializerMethodField(
        'get_avatar_url',
        required=False
    )
    is_subscribed = serializers.SerializerMethodField(default=False)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_avatar_url(self, obj):
        """Метод получает URL изображения."""
        if obj.avatar:
            return obj.avatar.url
        return None

    def get_is_subscribed(self, obj):
        """
        Метод проверяет, подписан ли текущий пользовтаель
        на другого пользователя.
        """
        if not self.context.get('request'):
            return False
        current_user = self.context.get('request').user
        if current_user.is_authenticated:
            return Subscription.objects.filter(
                current_user=current_user,
                user=obj.id
            ).exists()
        return False


class UserShowSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения объекта модели
    User после его создания.
    """

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания объекта модели User."""

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_username(self, value):
        """Метод проверяет юзернейм пользователя."""
        username_pattern = r"^[\w.@+-]+\Z"
        if value == "me":
            raise serializers.ValidationError(
                "Недопустимое имя пользователя",
            )
        if not re.match(username_pattern, value):
            raise serializers.ValidationError(
                "Недопустимые символы в имени пользователя",
            )
        return value

    def to_representation(self, user):
        """Метод изменяет сериализатор для отображение объекта User.
        Используется при формировании ответа на POST запрос."""
        serializer = UserShowSerializer(user)
        return serializer.data


class AvatarUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления аватара текущего пользователя."""
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)

    def get_avatar_url(self, obj):
        """Метод получает URL изображения."""
        if obj.avatar:
            return obj.avatar.url
        return None

    def to_representation(self, instance):
        """
        Метод изменяет формат вывода данных для модели пользователя,
        преобразуя аватар в ссылку на изображение."""
        representation = super().to_representation(instance)
        avatar_url = instance.avatar.url
        representation['avatar'] = avatar_url
        return representation


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
    """Сериализатор для модели IngredientRecipe при создании рецепта."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения объекта модели Recipe."""
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientRecipeSerializer(
        source='ingredientrecipe', many=True
    )
    is_favorited = serializers.SerializerMethodField(default=False)
    is_in_shopping_cart = serializers.SerializerMethodField(default=False)
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

    def get_is_favorited(self, obj):
        """
        Метод проверяет, есть ли рецепт в избранном
        у текущего пользователя.
        """
        if 'request' not in self.context:
            return False
        current_user = self.context['request'].user
        if current_user.is_authenticated:
            return Favorite.objects.filter(
                current_user=current_user,
                recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """
        Метод проверяет, есть ли рецепт в списке покупок
        у текущего пользователя.
        """
        if 'request' not in self.context:
            return False
        current_user = self.context['request'].user
        if current_user.is_authenticated:
            return ShoppingList.objects.filter(
                current_user=current_user,
                recipe=obj
            ).exists()
        return False

    def get_image_url(self, obj):
        """Метод получает URL изображения."""
        if obj.image:
            return obj.image.url
        return None


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания или изменения объекта Recipe."""
    ingredients = IngredientRecipeSerializer(
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        """
        Метод проверяет корректность введеных данных
        для ингредиентов и тегов.
        """
        for field in ['ingredients', 'tags']:
            if field not in self.initial_data:
                raise serializers.ValidationError(
                    {field: ['Это поле обязательно для заполнения.']},
                    code='required'
                )
        ingredients = self.initial_data.get('ingredients')
        igredients_ids = set()

        if ingredients == []:
            raise serializers.ValidationError(
                {'ingredients': ['Это поле обязательно для заполнения.']},
                code='required'
            )

        for ingredient in ingredients:
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise serializers.ValidationError(
                    {'ingredients': ['Такого ингредиента не существует.']},
                    code='invalid'
                )

            if ingredient['id'] in igredients_ids:
                raise serializers.ValidationError(
                    {'ingredients': ['Вы уже указали данный ингредиент.']},
                    code='invalid'
                )
            igredients_ids.add(ingredient['id'])

        if self.initial_data.get('tags') == []:
            raise serializers.ValidationError(
                {'tags': ['Это поле обязательно для заполнения.']},
                code='required'
            )

        if len(data.get('tags')) != len(set(data.get('tags'))):
            raise serializers.ValidationError(
                {'tags': ['Вы уже указали данный тег.']},
                code='invalid'
            )

        data['ingredients'] = ingredients
        return data

    def create(self, validated_data):
        """Переопределят метод для создания объекта модели Recipe.
        и создает соответствующие записи в связанных таблицах
        (для Tag и Ingredient).
        """
        image = validated_data.pop('image')
        author = self.context['request'].user
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(
            author=author,
            image=image,
            **validated_data
        )
        recipe.tags.set(tags_data)

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
        """Переопределяет метод для изменения объекта модели Recipe."""
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )

        if 'tags' not in validated_data:
            instance.save()
        else:
            instance.tags.clear()
            tags_data = self.initial_data.get('tags')
            instance.tags.set(tags_data)

        if 'ingredients' not in validated_data:
            instance.save()
        else:
            ingredients_data = validated_data.pop('ingredients')
            IngredientRecipe.objects.filter(recipe=instance).all().delete()
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
    """
    Сериализатор для модели Recipe.
    Используется при формирование ответов на запросы.
    """
    image = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image_url(self, obj):
        """Метод получает URL изображения."""
        if obj.image:
            return obj.image.url
        return None

    def validate(self, data):
        """
        Метод проверяет данные для рецепта при добавлении и
        удаление из списока покупок или в избранного.
        """
        print(self.context['request'].path)
        current_user = self.context['request'].user
        recipe_id = self.initial_data['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        path = self.context['request'].path

        if 'shopping_cart' in path:
            item = ShoppingList.objects.filter(
                current_user=current_user.id,
                recipe=recipe
            )
        else:
            item = Favorite.objects.filter(
                current_user=current_user.id,
                recipe=recipe
            )

        if self.context['request'].method == 'POST' and item:
            raise serializers.ValidationError(
                'Вы уже добавили этот рецепт.',
            )

        if self.context['request'].method == 'DELETE' and not item:
            raise serializers.ValidationError(
                'Ошибка удаления рецепта.',
            )
        return data


class ShortLinkRecipeSeriealizer(serializers.ModelSerializer):
    """Сериализатор для модели ShortLink."""

    class Meta:
        model = ShortLinkRecipe
        fields = ('short_link',)


class SubcriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Subscription."""
    id = serializers.ReadOnlyField(source='user.id')
    email = serializers.ReadOnlyField(source='user.email')
    username = serializers.ReadOnlyField(source='user.username')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField(
        'get_avatar_url',
        required=False
    )

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )

    def get_avatar_url(self, obj):
        """Метод получает URL изображения."""
        if obj.user.avatar:
            return obj.user.avatar.url
        return None

    def get_is_subscribed(self, obj):
        """
        Метод проверяет, подписан ли текущий пользовтаель
        на другого пользователя.
        """
        if obj.current_user.is_authenticated:
            return Subscription.objects.filter(
                current_user=obj.current_user,
                user=obj.user
            ).exists()

    def get_recipes(self, obj):
        """
        Получает список рецептов, созданных пользователем,
        на котрого подписан текущий пользователь.
        """
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit', None
        )
        if recipes_limit:
            recipes = Recipe.objects.filter(
                author=obj.user)[:int(recipes_limit)]
            serializer = RecipeResponseSerializer(recipes, many=True)
            return serializer.data
        else:
            recipes = Recipe.objects.filter(author=obj.user)
            serializer = RecipeResponseSerializer(recipes, many=True)
            return serializer.data

    def get_recipes_count(self, obj):
        """
        Получает количество рецептов, созданных пользователем,
        на котрого подписан текущий пользователь.
        """
        return Recipe.objects.filter(author=obj.user).count()
