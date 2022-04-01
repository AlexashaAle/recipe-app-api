from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

# первый параметр это приложение, второй идентификатор юрл в приложении
RECIPES_URL = reverse('recipe:recipe-list')

# создаем допфунк для добавления айди к юрл


def detail_url(recipe_id):
    """Return recipe deteils url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name="main course"):
    """creating the sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingrdient(user, name="Cinamon"):
    """creating the sample Ingredient"""
    return Ingredient.objects.create(user=user, name=name)


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

    def test_view_recipe_detail(self):
        """Test viewing the recipe details"""
        recipe = sample_recipe(user=self.user)
        # добавление тега к рецепту
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingrdient(user=self.user))

        # задаем ссылку для запрса
        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test create recipe"""
        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': 5.00
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        #  в джанго в ответе возвращается словарь
        recipe = Recipe.objects.get(id=res.data['id'])
        # перечисляет все элементы в словаре
        for key in payload.keys():
            # сравниваем каждое значение ключа в ответе с тем что в системе
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tag(self):
        # создаем два тега
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')
        # создаем рецепт с тегами
        payload = {
            'title': 'Avocsdo lime cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00
        }
        # добавляем рецепт в систему
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # отправляем запрос для получения созданного рецепта
        recipe = Recipe.objects.get(id=res.data['id'])
        # извлекаем теги
        tags = recipe.tags.all()
        # проверяем количество возвращенных тегов
        self.assertEqual(tags.count(), 2)
        # проверям теги в списке тегов
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients"""
        ingredient1 = sample_ingrdient(user=self.user, name="Prawns")
        ingredient2 = sample_ingrdient(user=self.user, name="Ginger")
        payload = {
            "title": 'Thai prawn red curry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 20,
            'price': 7.00
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        # извлекаем теги
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updating te recipe with patch"""
        # patch - обновляет только поля заданные в запросе
        # создаем рецепт
        recipe = sample_recipe(user=self.user)
        # добавляем тег к рецепту
        recipe.tags.add(sample_tag(user=self.user))
        # содаем новый тег для проверки замены тега
        new_tag = sample_tag(user=self.user, name='Curry')
        # задаем поля для обновления рецепта
        payload = {'title': 'Chiken tikka', 'tags': new_tag.id}
        # создаем ссылку включающую айди рецепта
        url = detail_url(recipe.id)
        # отправляем патч запрос
        # здесь мы не сохраняем ответ,  выполняем проверку через дб
        self.client.patch(url, payload)
        # обновляем информацию в рецепте через базу данных
        # где-бы вносились изменения они не обнавлcяться  до вызова функциии
        recipe.refresh_from_db()
        # проверяем соответвие рецепта из дб и загружанных полей
        self.assertEqual(recipe.title, payload['title'])
        # выгружаем все теги
        tags = recipe.tags.all()
        # проверяем количество тегов
        # должно быть равным одному, тек обновился а не прибавился
        self.assertEqual(len(tags), 1)
        # проверяем что тег замене на новый тег
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Update the recipe with put"""
        # пут заменяет весь обьект целиком, без сохранения предыдущих полей
        # создаем пробный рецепт
        recipe = sample_recipe(user=self.user)
        # добавляем в него пробный тег
        recipe.tags.add(sample_tag(user=self.user))
        # добаляем Поля
        payload = {
            'title': 'Spagetti carbonara',
            'time_minutes': 25,
            'price': 5.00
        }
        # создаем юрл с дбавлением айди рецепта
        url = detail_url(recipe.id)
        # отправляем запрос
        self.client.put(url, payload)

        recipe.refresh_from_db()
        # проверяем соответствие полей в бд и в запросе
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        # загружаем теги рецепта из базы данных
        tags = recipe.tags.all()
        # в рецепте обнавленном черз пут тегов быть не должно
        self.assertEqual(len(tags), 0)
