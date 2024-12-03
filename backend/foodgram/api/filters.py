import django_filters

from recipes.models import Favorite, Tag, Recipe


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для модели Recipe.
    Фильтр позволяет фильтровать рецепты по различным полям.
    Фильтр позволяет: показывать только рецепты, находящиеся
    в списке избранного, находящиеся в списке покупок;
    показывать рецепты только автора с указанным id;
    показывать рецепты только с указанными тегами (по slug).
    """
    author = django_filters.NumberFilter(
        field_name='author',
        lookup_expr='exact'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug', to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorite = django_filters.BooleanFilter(method='filter_is_favorite')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def filter_is_favorite(self, queryset, name, value):
        current_user = self.request.user
        if value is not None:
            if value:
                return Favorite.objects.filter(current_user=current_user.id)
            else:
                return queryset