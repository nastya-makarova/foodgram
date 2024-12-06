from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FoodgramUser, Subscription


@admin.register(FoodgramUser)
class UserAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'avatar'
    )

    list_editable = (
        "first_name",
        "last_name",
        "email",
    )


UserAdmin.fieldsets += (
    ('Аватар', {'fields': ('avatar',)}),

)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('current_user', 'user')
