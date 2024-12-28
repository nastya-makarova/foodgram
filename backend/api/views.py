from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404, redirect
from djoser.permissions import CurrentUserOrAdmin
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .filters import RecipeFilter
from .pagination import LimitPagePagination
from .permissions import UnauthorizedOrAdmin, RecipePermisssion
from .serializers import (
    AvatarUpdateSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    RecipeResponseSerializer,
    ShortLinkRecipeSeriealizer,
    SubcriptionSerializer,
    TagSerializer,
    UserSerializer,
    UserCreateSerializer
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


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с моделью Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с моделью Ingredient."""
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        keyword = self.request.query_params.get('name', '')
        queryset = Ingredient.objects.filter(name__icontains=keyword)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с моделью Recipe."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPagePagination
    http_method_names = ["get", "post", "patch", "delete"]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (RecipePermisssion,)

    def get_serializer_class(self):
        """Метод определяет, какой сериализатор использовать.
        RecipeSerializer для операций 'list' и 'retrieve'.
        RecipeCreateSerializer для других действий (например, 'create')."""
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(
        methods=['get'],
        detail=True,
        url_path='get-link',
        permission_classes=(permissions.AllowAny,)
    )
    def get_recipe_short_link(self, request, pk=None):
        """Метод позволяет получить короткую ссылку для рецепта."""
        recipe = self.get_object()
        short_link, created = ShortLinkRecipe.objects.get_or_create(
            recipe=recipe
        )
        serializer = ShortLinkRecipeSeriealizer(short_link)
        short_link_url = (
            f'{settings.HOST_NAME}s/{serializer.data["short_link"]}'
        )
        return Response({
            'short-link': short_link_url
        })

    @action(
        methods=['get'],
        url_path='download_shopping_cart',
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_shopping_cart(self, request):
        """Метод для загрузки списка покупок в формате TXT.
        Метод получает список покупок для текущего пользователя
        и создает текстовый файл.
        """
        recipes_for_shopping = ShoppingList.objects.filter(
            current_user=request.user
        )
        items = {}
        for recipe in recipes_for_shopping:
            ingredients = IngredientRecipe.objects.filter(recipe=recipe.recipe)
            for ingredient in ingredients:
                ing_obj = Ingredient.objects.filter(
                    id=ingredient.ingredient.id
                ).first()
                amount = ingredient.amount
                if ing_obj.name not in items:
                    items[ing_obj.name] = {
                        'amount': amount,
                        'measurement_unit': ing_obj.measurement_unit
                    }
                else:
                    items[ing_obj.name]['amount'] += amount

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        for name, data in items.items():
            list_item = (
                f"{name} - {data['amount']} {data['measurement_unit']}"
            )
            response.write(f"{list_item}\n")
        return response

    @action(
        methods=['post', 'delete'],
        url_path='shopping_cart',
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def add_and_delete_shopping_cart(self, request, pk):
        """
        Метод добавляет рецепт в список покупок пользователя.
        Или удаляет рецепт из списка покупок пользователя.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        current_user = request.user

        data = {'id': recipe.id,
                'name': recipe.name,
                'image': recipe.image,
                'cooking_time': recipe.cooking_time}
        serializer = RecipeResponseSerializer(
            data=data,
            context={'request': request})

        if serializer.is_valid():
            if request.method == 'POST':
                shopping_list = ShoppingList.objects.create(
                    current_user=current_user,
                    recipe=recipe
                )
                serializer = RecipeResponseSerializer(shopping_list.recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

            if request.method == 'DELETE':
                shopping_list = ShoppingList.objects.filter(
                    current_user=current_user,
                    recipe=recipe).first()
                shopping_list.delete()
                return Response(
                    {'detail': 'Рецепт успешно удален из списка покупок.'},
                    status=status.HTTP_204_NO_CONTENT
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['post', 'delete'],
        url_path='favorite',
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def add_and_delete_favorite(self, request, pk):
        """
        Метод добавляет рецепт в избранное пользователя.
        Или удаляет рецепт из избранного пользователя.
        """
        recipe = get_object_or_404(Recipe, id=pk)
        current_user = request.user

        data = {'id': recipe.id,
                'name': recipe.name,
                'image': recipe.image,
                'cooking_time': recipe.cooking_time}
        serializer = RecipeResponseSerializer(
            data=data,
            context={'request': request}
        )

        if serializer.is_valid():
            if request.method == 'POST':
                favorite_recipe = Favorite.objects.create(
                    current_user=current_user,
                    recipe=recipe
                )
                serializer = RecipeResponseSerializer(favorite_recipe.recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)

            if request.method == 'DELETE':
                favorite_recipe = Favorite.objects.filter(
                    current_user=current_user,
                    recipe=recipe).first()
                favorite_recipe.delete()
                return Response(
                    {'detail': 'Рецепт успешно удален из избранного.'},
                    status=status.HTTP_204_NO_CONTENT
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FoodgramUserViewSet(UserViewSet):
    """ViewSet для работы с моделью User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPagePagination
    permission_classes = ()

    def get_serializer_class(self):
        """Метод определяет, какой сериализатор использовать.
        UserSerializer для операций 'list' и 'retrieve'.
        UserCreateSerializer для 'create')."""
        if self.action == 'set_password':
            return SetPasswordSerializer

        if self.action in ('list', 'retrieve', 'me'):
            return UserSerializer
        return UserCreateSerializer

    @action(
        methods=['put', 'delete'],
        url_path='me/avatar',
        detail=False,
        permission_classes=(CurrentUserOrAdmin,)
    )
    def update_avatar(self, request):
        """Метод изменяет аватара текущего пользователя."""

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

    @action(
        methods=['get'],
        url_path='subscriptions',
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=SubcriptionSerializer
    )
    def get_subcriptions(self, request):
        """Метод получает все подписки текущего пользователя."""
        subscriptions = Subscription.objects.filter(
            current_user=request.user).order_by('id')
        paginated_subscriptions = self.paginator.paginate_queryset(
            subscriptions,
            request
        )
        serializer = SubcriptionSerializer(
            paginated_subscriptions,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        url_path='subscribe',
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def add_and_delete_subscribe(self, request, id=None):
        """
        Метод добавляет и удаляет пользователя из
        списка подписок текущего пользователя.
        """
        user = get_object_or_404(User, id=id)
        current_user = request.user
        data = {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
        serializer = SubcriptionSerializer(
            data=data,
            context={'request': request}
        )
        if serializer.is_valid():
            if request.method == 'POST':
                subscription = Subscription.objects.create(
                    current_user=current_user,
                    user=user
                )
                serializer = SubcriptionSerializer(
                    subscription,
                    context={'request': request}
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

            if request.method == 'DELETE':
                subscription = Subscription.objects.filter(
                    current_user=current_user,
                    user=user
                ).first()
                subscription.delete()
                return Response({"detail": "Успешная отписка."},
                                status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.action == 'me':
            return (permissions.IsAuthenticated(),)

        if self.action == 'create':
            return (UnauthorizedOrAdmin(),)

        return super().get_permissions()


def redirect_to_recipe(request, short_link):
    try:
        short_link = ShortLinkRecipe.objects.get(short_link=short_link)
        return redirect(f'/recipes/{short_link.recipe.id}')
    except ShortLinkRecipe.DoesNotExist:
        return redirect('/')
