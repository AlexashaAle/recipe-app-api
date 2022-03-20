# захват можели юзер
from django.contrib.auth import get_user_model
# содание ссылки
from django.urls import reverse
# тестовый классgtht
from django.test import TestCase

# статус HTTP
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test publicly avalible tags API"""

    def setUp(self):
        # задаем не авторизироаного юзера
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving the tags """
        # тест авторизация необхадима для извлечения тегов

        res = self.client.get(TAGS_URL)
        # проверям что теги не доступны для неаторизованного позьзователя
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """The authorized user tags API """
    #  тесты для аторизованных пользователей

    # функция которая будет выполять перед каждым тестом
    def setUp(self):
        # создаем тестового юзера
        self.user = get_user_model().objects.create_user(
            "test@something.com",
            "pass122345"
        )
        self.client = APIClient()
        # авторизуем созданного юзера
        self.client.force_authenticate(self.user)

    def test_retrive_tags(self):
        """Test retrive tags"""
        #  создаем теги от имени нового юзера
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        # отправляем запрос который должен вернуть наши теги
        res = self.client.get(TAGS_URL)
        # распрееляет теги в алфавитном порядке
        tags = Tag.objects.all().order_by("-name")
        # many = True  позволяет сериализорать большо одного обьекта за раз
        serializer = TagSerializer(tags, many=True)
        # сравниваем коды ответа
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # проверяем если возвращенные данные сответвуют данным в системе
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for authorized user"""
    # проверяет что ты извлекаются только для атворизованного пользователя
    # создаем не авторизованного пользователя
        user2 = get_user_model().objects.create_user(
            "someone@something.com",
            'testpass'
        )
        # создаем тег от имени не авторизованного пользователя
        Tag.objects.create(user=user2, name="Fruity")
        tag = Tag.objects.create(user=self.user, name="Comfort Food")

        res = self.client.get(TAGS_URL)

        # проверяет код ответа
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # проверям что система вернула только один тег
        self.assertEqual(len(res.data), 1)
        # система вернула только тег соданнный автор. пользователем
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """ Test creating a new tag"""
        # задаем поля
        payload = {'name': "Test tag"}
        # отправляем пост запрос на создание тега
        self.client.post(TAGS_URL, payload)

        # exists() - возвращает правду или ложь
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        # проверяем если возвращена правда
        self.assertTrue(exists)

    def test_ctreate_tag_invalid(self):
        """Test creating a new tag with ivalid payload"""
        # задаем в поле имя пустую строку
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
