import base64
import re

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (Favorite,
                            Ingredient,
                            IngredientRecipe,
                            Recipe,
                            ShortLinkRecipe,
                            ShoppingList,
                            Tag,
                            TagRecipe,
                            User)
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
        if obj:
            current_user = obj
        else:
            current_user = self.context['request'].user
        if current_user.is_authenticated:
            return Subscription.objects.filter(
                current_user=current_user,
                user=obj
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
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

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
    """Сериализатор для модели Recipe. Используется при формирование ответов на запросы."""
    image = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image_url(self, obj):
        """Метод получает URL изображения."""
        if obj.image:
            return obj.image.url
        return None


class ShortLinkRecipeSeriealizer(serializers.ModelSerializer):
    """Сериализатор для модели ShortLink."""

    class Meta:
        model = ShortLinkRecipe
        fields = ('short_link',)


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ShoppingList."""
    recipe = RecipeResponseSerializer()

    class Meta:
        model = ShoppingList
        fields = ('recipe',)

    def to_representation(self, instance):
        """
        Метод изменяет формат вывода данных для рецепта,
        связанного со списком покупок.
        """
        representation = super().to_representation(instance)
        return representation['recipe']


class FavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Favorite."""
    recipe = RecipeResponseSerializer()

    class Meta:
        model = Favorite
        fields = ('recipe',)

    def to_representation(self, instance):
        """
        Метод переопределяет стандартное поведение сериализатора
        и возвращает только данные
        о рецепте, ассоциированном с объектом Favorite.
        """
        representation = super().to_representation(instance)
        return representation['recipe']


class UserSubscriptionSerializer(UserSerializer):
    """
    Сериализатор для модели User, является родительским
    сериализатором для сериализатора модели Подписок.
    """
    recipes = serializers.SerializerMethodField('get_recipes')
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, context):
        """
        Получает список рецептов, созданных пользователем,
        на котрого подписан текущий пользователь.
        """
        recipes = Recipe.objects.filter(author=context)
        serializer = RecipeResponseSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, context):
        """  
        Получает количество рецептов, созданных пользователем,
        на котрого подписан текущий пользователь.
        """
        return Recipe.objects.filter(author=context).count()


class SubcriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Subscription."""
    user = UserSubscriptionSerializer()

    class Meta:
        model = Subscription
        fields = ('user',)

    def to_representation(self, instance):
        """Метод изменяет тандартное поведение сериализатора."""
        representation = super().to_representation(instance)
        return representation['user']
