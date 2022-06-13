from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from recipe import serializers


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base view set for user owned recipe attributes"""
    # Создание базового класса обьеденяющего одинаковые елементы для тего и инг
    # авторизуемся с помощью токена
    authentication_classes = (TokenAuthentication,)
    # задаем разрешение только для авторизованных пользователей
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticatesd user only"""
        return self.queryset.filter(user=self.request.user).order_by("-name")

    def perform_create(self, serializer):
        """Create new object"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""
    # определяем набор запросов
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingrideents in data base"""

    # определяем запросы
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipe in data base"""

    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """retrive query set for autetheficated user"""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    # позволяет создавать изменения в действиях по умолчанию
    # detail -значит действие произвоодится над уже существующей ячейкой recipe
    # detail действие осуществлюейтся над юрл с существующим айди
    # Url_pach-путь для добавления файла
