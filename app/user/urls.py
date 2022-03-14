# позволяет задавать пути
from django.urls import path

from . import views

app_name = 'user'
# имя для идентификация
urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
]