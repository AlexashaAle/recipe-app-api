from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
# тестовый клиент для запросов
from rest_framework.test import APIClient
# модуль статусов http
from rest_framework import status
#  сохраняем в константу создание ссылки
CREATE_USER_URL = reverse('user:create')

# вспомогательная функия что бы не плодить юзеров
def create_user(**params):
    return get_user_model().objects.create_user(**params)

# Public для неавторизованых пользователей
class PublicUserApiTests(TestCase):
    """Test the Users Api( public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        # Поля для создания юзера
        payload = {
            'email': "test@something.com",
            'password': 'testpass',
            'name': 'testname'
        }
        # Отправляем пост запрос по http
        res = self.client.post(CREATE_USER_URL, payload)

        # Проверяем код ответа
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # Сохраняет ответ с инфо о юзере в переменную
        user = get_user_model().objects.get(**res.data)
        # проверяет соответвие пароля
        self.assertTrue(user.check_password(payload['password']))
        # проверяем что пароль зашифрован и не возвращается
        self.assertNotIn('password', res.date)

    def test_user_exists(self):
        """Test creating user that already exists fails"""

        payload = {'email': "test@something.com", 'password': 'testpass', 'name': 'testname'}
        # создаем юзера
        create_user(**payload)
        # отправляем запрос на создание созданного юера
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password must be more than 5 characters"""
        payload = {
            "email":"test@something.com", 'password': 'ass'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        # проверяем ответ от сервера при запросе с коротким паролем
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Проверяем что юзер возвращает лож, так как его не должно быть
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)