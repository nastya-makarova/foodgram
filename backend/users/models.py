from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
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
        validators=[UnicodeUsernameValidator()],
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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscription(models.Model):
    current_user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name='Текущий пользователь',
        related_name='follower'
    )
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name='Пользватель',
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'current_user'], name="unique_subscription"
            ),
        )

    def clean(self):
        if self.current_user == self.user:
            raise ValidationError("Вы не можете подписаться на самого себя.")

        if Subscription.objects.filter(
            current_user=self.current_user,
            user=self.user
        ).exists():
            raise ValidationError("Вы уже подписаны на этого пользователя.")

    def save(self, **kwargs):
        self.clean()
        super().save(**kwargs)
