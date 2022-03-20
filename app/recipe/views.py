from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag

from recipe import serializers


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    """Manage tags in the database"""
    # авторизуемся с помощью токена
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    # определяем набор запросов
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        """Return objects for the current authenticatesd user only"""
        # задаем фильтр результат выводился только авторизованным пользователям
        return self.queryset.filter(user=self.request.user).order_by('-name')

        # функция подключается с сериалайзеру и сохраняет обьекты
    def perform_create(self, serializer):
        """Create a new tag"""
        # сохранить обьект
        serializer.save(user=self.request.user)
