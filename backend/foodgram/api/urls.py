from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, FoodgramUserViewSet, APIDownloadShoppingList

users_v1 = DefaultRouter()

users_v1.register('users', FoodgramUserViewSet)

router_v1 = DefaultRouter()

router_v1.register('tags', TagViewSet)
router_v1.register('recipes', RecipeViewSet)
router_v1.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('recipes/download_shopping_cart/', APIDownloadShoppingList.as_view()),
    path('', include(router_v1.urls)),
    path('', include(users_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
