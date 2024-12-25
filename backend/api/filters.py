import django_filters
from recipes.models import Recipe, Tag


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
    is_favorited = django_filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """Метод фильтрует рецепты по наличию
        в избранном для текущего пользователя.
        """
        if self.request.user:
            current_user = self.request.user
        else:
            return None

        if current_user.is_authenticated and value is not None:
            if value == 1:
                return queryset.filter(
                    favorites__current_user=current_user.id
                )
            else:
                return queryset.exclude(
                    favorites__current_user=current_user.id
                )
        else:
            return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Метод фильтрует рецепты по наличию
        в списке покупок для текущего пользователя.
        """
        current_user = self.request.user

        if current_user.is_authenticated and value is not None:
            if value:
                return queryset.filter(
                    shopping_lists__current_user=current_user
                )
            else:
                return queryset.exclude(
                    shopping_lists__current_user=current_user.id
                )
        return queryset
