from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import ingredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """Test the publicly avalibler ingredients to access the endpoint"""

    def setUp(self):
        self.client = APIClient()

    def test_login_requert(self):
        """Test that login is requered to access the endpoint"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(TestCase):
    """Test private ingredientAPI"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@something.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingridients_list(self):
        """Test retrieving a list of ingredients"""

        # создаем ингридиенты
        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name='Salt')
        # отправляем запрос
        res = self.client.get(INGREDIENTS_URL)
        # подгружаем данные об ингридентах из системы
        ingredients = Ingredient.objects.all().order_by('-name')
        #  подгружаем сериализатор и задаемему мультиаргументы
        serializer = ingredientSerializer(ingredients, many=True)
        #  проверяем код ответа
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # сравниваем дату в базе и в ответе
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """ Test that ingredients for the authenticated user are return"""

        user2 = get_user_model().objects.create_user(
            "other@something.com",
            "passtest"
        )
        Ingredient.objects.create(user=user2, name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='Turmelic')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_succesfull(self):
        """Test create a new ingridiant succesfull"""
        # задаем поля
        payload = {'name': 'Testcarrot'}
        # оправляем пост запрос на создание ингридиента
        self.client.post(INGREDIENTS_URL, payload)
        # проверяем если ингридиент создан через exists
        exists = Ingredient.objects.filter(
                user=self.user,
                name=payload['name'],
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_ivalid(self):
        """test to creacte ingridien without name"""
        # задаем поля и в имени осталяем пустую строку
        payload = {'name': ''}
        # сохраняем ответ в переменную что бы стравнить его
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
