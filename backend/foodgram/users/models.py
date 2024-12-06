from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class FoodgramUser(AbstractUser):
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
