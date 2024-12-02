from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram.constants import (
    MAX_LENGTH_NAME,
    MAX_LENGTH_NAME_INGREDIENT,
    MAX_LENGTH_MEASURE_UNIT,
    MAX_LENGTH_NAME_TAG,
    MAX_LENGTH_SLUG
)


User = get_user_model()


class Ingredient(models.Model):
    """Модель для ингредиентов"""
    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_NAME_INGREDIENT,
        unique=True,
        help_text='Название ингредиента, не более 128 символов.'
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=MAX_LENGTH_MEASURE_UNIT,
        help_text='Единицы измерения, не более 64 символов.'

    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель для тегов."""
    name = models.CharField(
        'Имя тега',
        max_length=MAX_LENGTH_NAME_TAG,
        unique=True,
        help_text='Имя тега, не более 32 символов.'
    )
    slug = models.SlugField(
        'Слаг',
        max_length=MAX_LENGTH_SLUG,
        unique=True,
        help_text='Слаг, не более 32 символов'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель для рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )
    name = models.CharField(
        'Имя',
        max_length=MAX_LENGTH_NAME,
        help_text='Название рецепта, не более 256 символов.'
    )
    image = models.ImageField(
        'Фото рецепта',
        upload_to='recipes/images/',
        help_text='Картинка, закодированная в Base64'
    )
    text = models.TextField('Описание рецепта', help_text='Описание рецепта.')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты',
        help_text='Список ингредиентов.',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Тег',
        help_text='Список id тегов',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1, message="Значение времни должно быть не менее 1"
            )
        ],
        verbose_name='Время приготовления',
        help_text='Время приготовления (в минутах).'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Модель для связи между ингредиентами и рецептами.
    Связь между ингредиентами и рецептами многие-к-многим.
    """
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.FloatField(
        validators=[
            MinValueValidator(
                0.1, message='Укажите количество больше 0.'
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент и Рецепт'
        verbose_name_plural = 'Ингредиенты и Рецепты'


class TagRecipe(models.Model):
    """Модель для связи между тегами и рецептами.
    Связь между тегами и рецептами многие-к-многим.
    """
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Тег и Рецепт'
        verbose_name_plural = 'Теги и Рецепты'


class Favorite(models.Model):
    """Модель для избранных рецептов."""
    current_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Текущий пользователь',
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorites'
    )

    class Meta:
        unique_together = ('current_user', 'recipe')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class Subsrtictions(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользватель',
        related_name='follower'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('author', 'user')


class ShoppingList(models.Model):
    """Модель для списка покупок."""
    current_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Текущий пользователь',
        related_name='shopping_lists'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_lists'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
