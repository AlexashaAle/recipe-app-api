from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

# первый параметр это приложение, второй идентификатор юрл в приложении
RECIPES_URL = reverse('recipe:recipe-list')

# **params - переводит аргумет в словарь


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    # задаем значения по умолчанию

    defaults = {
        'title': 'sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    # обнавляем значения по умолчанию если они заданы в параметрах
    defaults.update(params)
    # **defaults переводим словарь в аргумент для функции
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_requert(self):
        """Test that login is requert to access the recipe"""
        # отправляем зарос от неавторизованного пользователя
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test recipe for authorized users"""

    def setUp(self):
        # задаем клиент для апи запросов
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
                "test@something.com"
                "testpass"
        )
        # авторизуемся в системе
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Test retrieving the list of recipe"""
        # тест извлечения рецептов
        # создаем два пробных рецепта
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        # задаем рецепты в переменную сортируя по дате создания
        recipes = Recipe.objects.all().order_by('-id')
        #  подгружаем сериализатор и задаемему мультиаргументы
        serializer = RecipeSerializer(recipes, many=True)
        # проверяем код ответа
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_limited_to_auth_user(self):
        """Test that recipe is limited for auth users"""

        user2 = get_user_model().objects.create_user(
            'someone@something.com'
            'secretpass'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        # подгружаем рецепты из сестемы и фильтруем из для залогиненого юзера
        recipes = Recipe.objects.filter(user=self.user)
        # добавляем many=True потому как обьект должен вернуться списком
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
