from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import FoodgramUser, Subscription
from recipes.models import Recipe


@admin.register(FoodgramUser)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'avatar',
        'password',
        'get_subscriptions_count',
        'get_recipes_count'
    )

    list_editable = (
        "first_name",
        "last_name",
        "email",
    )

    def get_subscriptions_count(self, obj):
        """Метод считает количество подписчиков пользователя."""
        return Subscription.objects.filter(user=obj).count()

    def get_recipes_count(self, obj):
        """Метод считает количество рецептов пользователя."""
        return Recipe.objects.filter(author=obj).count()

    get_subscriptions_count.short_short_description = (
        'Количество подписчиков пользователя.'
    )
    get_recipes_count.short_short_description = (
        'Количество рецептов пользователя.'
    )


UserAdmin.fieldsets += (
    ('Аватар', {'fields': ('avatar',)}),

)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('current_user', 'user')
