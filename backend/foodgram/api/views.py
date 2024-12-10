from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404, redirect
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet
from rest_framework import filters, mixins, status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

from .filters import RecipeFilter
from .serializers import (
    AvatarUpdateSerializer,
    FavoritesSerializer,
    IngredientSerializer,
    IngredientRecipeSerializer,
    IngredientRecipeCreateSerializer,
    RecipeSerializer, RecipeCreateSerializer,
    RecipeResponseSerializer,
    ShortLinkRecipeSeriealizer,
    ShoppingListSerializer,
    SubcriptionSerializer,
    TagSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserShowSerializer,
)

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    ShortLinkRecipe,
    Recipe,
    Tag,
    ShoppingList
)
from users.models import Subscription

User = get_user_model()


def redirect_to_recipe(request, short_link):
    try:
        short_link = ShortLinkRecipe.objects.get(short_link=short_link)
        return redirect('recipe-detail', pk=short_link.recipe.id)
    except ShortLinkRecipe.DoesNotExist:
        return redirect('/')


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с моделью Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с моделью Ingredient."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)

    def get_queryset(self):
        keyword = self.request.query_params.get('name', '')
        queryset = Ingredient.objects.filter(name__icontains=keyword)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с моделью Recipe."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    http_method_names = ["get", "post", "patch", "delete"]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Метод определяет, какой сериализатор использовать.
        RecipeSerializer для операций 'list' и 'retrieve'.
        RecipeCreateSerializer для других действий (например, 'create')."""
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(detail=True, url_path='get-link')
    def get_recipe_short_link(self, request, pk=None):
        """Метод позволяет получить короткую ссылку для рецепта."""
        recipe = self.get_object()
        short_link, created = ShortLinkRecipe.objects.get_or_create(
            recipe=recipe
        )
        serializer = ShortLinkRecipeSeriealizer(short_link)
        short_link_url = f'http://127.0.0.1:8000/s/{serializer.data["short_link"]}'
        return Response({
            'short_link': short_link_url
        })


class FoodgramUserViewSet(UserViewSet):
    """ViewSet для работы с моделью User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        """Метод определяет, какой сериализатор использовать.
        UserSerializer для операций 'list' и 'retrieve'.
        UserCreateSerializer для 'create')."""
        if self.action == 'set_password':
            return SetPasswordSerializer

        if self.action in ('list', 'retrieve'):
            return UserSerializer
        return UserCreateSerializer

    @action(
        methods=['put', 'delete'],
        url_path='me/avatar',
        detail=False
    )
    def update_avatar(self, request):
        """Метод для изменения аватара текущего пользователя."""

        current_user = request.user
        if request.method == 'DELETE':
            if current_user.avatar:
                current_user.avatar.delete()
                current_user.save()
                return Response(
                    {'detail': 'Аватар успешно удален.'},
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    {'detail': 'Аватар не найден.'},
                    status=status.HTTP_404_NOT_FOUND
                )

        serializer = AvatarUpdateSerializer(current_user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIDownloadShoppingList(APIView):
    """View-класс для загрузки списка покупок в формате TXT."""
    def create_txt_file(self, items):
        """Создание TXT файла."""
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        for item in items:
            list_item = (
                f"{item['name']} - {item['amount']} {item['measurement_unit']}"
            )
            response.write(f"{list_item}\n")
        return response

    def get(self, request):
        """
        Метод получает список покупок для текущего пользователя
        и создает текстовый файл.
        """
        recipes_for_shopping = ShoppingList.objects.filter(
            current_user=request.user
        )
        items = []
        for recipe in recipes_for_shopping:
            ingredients = IngredientRecipe.objects.filter(recipe=recipe.recipe)
            for ingredient in ingredients:
                ing_obj = Ingredient.objects.filter(
                    id=ingredient.ingredient.id
                ).first()
                amount = ingredient.amount
                if len(items) == 0:
                    items.append({
                        'name': ing_obj.name,
                        'amount': amount,
                        'measurement_unit': ing_obj.measurement_unit
                    })
                for i in range(len(items)):
                    if ing_obj.name in items[i].values():
                        items[i]['amount'] += amount
                        break
                    else:
                        items.append({
                            'name': ing_obj.name,
                            'amount': amount,
                            'measurement_unit': ing_obj.measurement_unit
                        })
        return self.create_txt_file(items)


class APIShoppingList(APIView):
    """
    View-класс для добавления и удаления рецептов
    из списка покупок пользователя.
    """
    def post(self, request, pk):
        """Добавление рецепта в список покупок пользователя."""
        recipe = get_object_or_404(Recipe, id=pk)
        current_user = request.user
        shopping_list = ShoppingList.objects.create(
            current_user=current_user,
            recipe=recipe
        )
        serializer = ShoppingListSerializer(shopping_list)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        """Удаление рецепта в список покупок пользователя."""
        current_user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        shopping_list = get_object_or_404(
            ShoppingList,
            current_user=current_user,
            recipe=recipe
        )
        if shopping_list:
            shopping_list.delete()
            return Response(
                {'detail': 'Рецепт успешно удален из списка покупок.'},
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            {'detail': 'Ошибка удаления из списка покупок.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class APIFavorite(APIView):
    """
    View-класс для добавления и удаления рецептов
    из избранного пользователя.
    """
    def post(self, request, pk):
        """Добавление рецепта в избранное пользователя."""
        recipe = get_object_or_404(Recipe, id=pk)
        favorite_recipe = Favorite.objects.create(
            current_user=request.user,
            recipe=recipe
        )
        serializer = FavoritesSerializer(favorite_recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        """Удаление рецепта в избранное пользователя."""
        recipe = get_object_or_404(Recipe, id=pk)
        favorite_recipe = get_object_or_404(
            Favorite,
            current_user=request.user,
            recipe=recipe
        )
        if favorite_recipe:
            favorite_recipe.delete()
            return Response(
                {'detail': 'Рецепт успешно удален из избранного.'},
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {'detail': 'Ошибка удаления из избранного.'},
                status=status.HTTP_204_NO_CONTENT
            )


class APIListSubscriptions(ListAPIView):
    """View-класс для получения списка подписок текущего пользователя."""
    pagination_class = PageNumberPagination
    serializer_class = SubcriptionSerializer

    def get_queryset(self):
        """Метод получает все подписки текущего пользователя."""
        return Subscription.objects.filter(
            current_user=self.request.user
        ).order_by('id')


class APISubscription(APIView):
    """
    View-класс для добавления и удаления пользователя из 
    списка подписок текущего пользователя.
    """
    def post(self, request, pk):
        """Добавление пользователя в подписки текущего пользователя."""
        user = get_object_or_404(User, id=pk)
        subscription = Subscription.objects.create(
            current_user=request.user,
            user=user
        )
        serializer = SubcriptionSerializer(subscription, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        """Удаление пользователя из подпискок текущего пользователя."""
        user = get_object_or_404(User, id=pk)
        subscription = get_object_or_404(
            Subscription,
            current_user=request.user,
            user=user
        )
        if subscription:
            subscription.delete()
            return Response(
                {"detail": "Успешная отписка."},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {"detail": "Стпаница не найдена."},
            status=status.HTTP_404_NOT_FOUND
        )
