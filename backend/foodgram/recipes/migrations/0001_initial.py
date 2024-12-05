# Generated by Django 3.2.16 on 2024-11-29 18:00

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название ингредиента, не более 128 символов.', max_length=128, unique=True, verbose_name='Название')),
                ('measurement_unit', models.CharField(help_text='Единицы измерения, не более 64 символов.', max_length=64, unique=True, verbose_name='Единицы измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'unique_together': {('name', 'measurement_unit')},
            },
        ),
        migrations.CreateModel(
            name='IngredientRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.ingredient')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Название рецепта, не более 256 символов.', max_length=256, verbose_name='Имя')),
                ('image', models.ImageField(help_text='Картинка, закодированная в Base64', upload_to='recipes/images/', verbose_name='Фото рецепта')),
                ('text', models.TextField(help_text='Описание рецепта.', verbose_name='Описание рецепта')),
                ('cooking_time', models.PositiveSmallIntegerField(help_text='Время приготовления (в минутах).', validators=[django.core.validators.MinValueValidator(1, message='Значение времни должно быть не менее 1')], verbose_name='Время приготовления')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('ingredients', models.ManyToManyField(help_text='Список ингредиентов.', related_name='recipes', through='recipes.IngredientRecipe', to='recipes.Ingredient', verbose_name='Ингредиенты')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('-pub_date',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Имя тега, не более 32 символов.', max_length=32, unique=True, verbose_name='Имя тега')),
                ('slug', models.SlugField(help_text='Слаг, не более 32 символов', max_length=32, unique=True, verbose_name='Слаг')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
        migrations.CreateModel(
            name='TagRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.tag')),
            ],
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='Список id тегов', related_name='recipes', through='recipes.TagRecipe', to='recipes.Tag', verbose_name='Тег'),
        ),
        migrations.AddField(
            model_name='ingredientrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe'),
        ),
        migrations.CreateModel(
            name='Subsrtictions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='Пользватель')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
                'unique_together': {('author', 'user')},
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='recipes.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'Избранное',
                'verbose_name_plural': 'Избранные',
                'unique_together': {('author', 'recipe')},
            },
        ),
    ]
