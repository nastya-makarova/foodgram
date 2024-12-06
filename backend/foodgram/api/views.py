from http import HTTPStatus

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import redirect
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from .filters import RecipeFilter
from .serializers import (
    IngredientSerializer,
    IngredientRecipeSerializer,
    IngredientRecipeCreateSerializer,
    RecipeSerializer, RecipeCreateSerializer,
    RecipeResponseSerializer,
    ShortLinkRecipeSeriealizer,
    TagSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserShowSerializer
)
from recipes.models import Ingredient, ShortLinkRecipe, Recipe, Tag

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


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """ViewSet для работы с моделью User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        """Метод определяет, какой сериализатор использовать.
        UserSerializer для операций 'list' и 'retrieve'.
        UserCreateSerializer для 'create')."""
        if self.action in ('list', 'retrieve'):
            return UserSerializer
        return UserCreateSerializer

    @action(
        methods=['get'],
        detail=False,
        url_path='me'
    )
    def get_me(self, request):
        print('Hello!')
        serializer = UserSerializer(request.user, context={'request': request})
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
