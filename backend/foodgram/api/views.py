from django.shortcuts import render
from rest_framework import viewsets

from .serializers import TagSerializer
from recipes.models import Recipe, Tag


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с моделью Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer