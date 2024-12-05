from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import redirect
from rest_framework.response import Response
from rest_framework import viewsets
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
    TagSerializer
)
from recipes.models import Ingredient, ShortLinkRecipe, Recipe, Tag


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
        recipe = self.get_object()
        short_link, created = ShortLinkRecipe.objects.get_or_create(recipe=recipe)
        print(short_link)
        serializer = ShortLinkRecipeSeriealizer(short_link)
        print(serializer.data)
        short_link_url = f'http://127.0.0.1:8000/s/{serializer.data["short_link"]}'
        print(short_link_url)
        return Response({
            'short_link': short_link_url
        })
