from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram.constants import MAX_LENGTH_NAME

User = get_user_model()


class Ingredient(models.Model):
    pass


class Tag(models.Model):
    pass


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
        help_text='Название рецепта, не более 256 символов'
    )
    image = models.ImageField(
        'Фото рецепта',
        upload_to='recipes/images/',
        help_text='Картинка, закодированная в Base64'
    )
    text = models.TextField('Описание рецепта', help_text='Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient, 
        through='IngredientRecipe',
        verbose_name='Ингредиенты',
        help_text='Список ингредиентов',
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
        help_text='Время приготовления (в минутах)'
    )


class IngredientRecipe(models.Model):
    """Модель для связи между ингредиентами и рецептами.
    Связь между ингредиентами и рецептами многие-к-многим.
    """
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class TagRecipe(models.Model):
    """Модель для связи между тегами и рецептами.
    Связь между тегами и рецептами многие-к-многим.
    """
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

