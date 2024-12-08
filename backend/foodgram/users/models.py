from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.constants import MAX_LENGTH_EMAIL, MAX_LENGTH_FOR_USER


class FoodgramUser(AbstractUser):
    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        verbose_name='Адрес электронной почты пользовтаеля'
    )
    username = models.CharField(
        max_length=MAX_LENGTH_FOR_USER,
        unique=True,
        verbose_name='Уникальный юзернейм'
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_FOR_USER,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_FOR_USER,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=MAX_LENGTH_FOR_USER,
        verbose_name='Пароль'
    )

    avatar = models.ImageField(
        'Аватар пользователя',
        upload_to='users/images/',
        help_text='Аватар пользователя, закодированный в Base64',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


User = get_user_model()


class Subscription(models.Model):
    current_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Текущий пользователь',
        related_name='follower'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользватель',
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('current_user', 'user')
