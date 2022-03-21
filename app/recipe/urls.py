from django.urls import path, include
from rest_framework.routers import DefaultRouter
# DefaultRouter при наличии окружения с множество юрл
# автоматически создает соответвующие ссылки
from recipe import views


router = DefaultRouter()
# регистрируем наши ссылки и соотносим их с окружением
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)

app_name = 'recipe'

# задаем шаблоны юрл

urlpatterns = [path('', include(router.urls))]
