# Generated by Django 3.2.16 on 2024-12-05 12:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_shortlink'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ShortLink',
            new_name='ShortLinkRecipe',
        ),
        migrations.AlterModelOptions(
            name='shortlinkrecipe',
            options={'verbose_name': 'Короткая ссылка для рецепта', 'verbose_name_plural': 'Короткие ссылки для рецепта'},
        ),
    ]
