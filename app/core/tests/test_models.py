from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email="test@something.com", password="testpass"):
    # создаем тестового юзера для проверки системы
    """Create the sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating the new user with email succesesful"""
        email = "foranytestsme@gmail.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalaized(self):
        """Test the email for a new user is normalized"""
        email = "foanytestme@GMAil.com"
        user = get_user_model().objects.create_user(email, "test123")

        self.assertEqual(user.email, email.lower())

    def test_new_user_inavalid_email(self):
        """Test creating the user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "test123")

    def test_create_new_superuser(self):
        """Test creating the new superuser """
        user = get_user_model().objects.create_superuser(
            "test@gmail.com",
            "test123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
    # проверям создался ли тег и строка ли он
        tag = models.Tag.objects.create(
            user=sample_user(),
            name="Vegan"
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """test ingredient str representation"""
        # проверяем если модель созданна и отображается коректно
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """"test recipe string reresentetion"""

        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title="Pasta",
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch("uuid.uuid4")
    # создаем уникальный айди версия 4
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image saved in the correct location"""
        # Симулируем изображение и сохраняем его
        # прверяем что возвращенная строка соответствует заданном пути
        uuid = 'test-uuid'
        #  каждый раз при вызове uuid переписыает функцию и возвращает тестовый
        mock_uuid.return_value = uuid
        # подгружаем из моделей пока не созданную пукцию возвращающую путь
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        # задаем ожидаемы путь
        exp_path = f"uploads/recipe/{uuid}.jpg"
        # проверяем соответствие
        self.assertEqual(file_path, exp_path)
