import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.conf import settings


def recipe_image_file_path(instace, filename):
    """Generete file path for new recipe image"""
    # вытаскиваем из имени файла рgthtасширение путем создания списка
    ext = filename.split(".")[-1]
    # создаем новое имя файла
    filename = f"{uuid.uuid4()}.{ext}"
    # возвращаем путь, join  позволяет соеденять разные переменные в пути
    return os.path.join('uploads/recipe/', filename)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new User"""
        if not email:
            raise ValueError("Users must have the email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and saves new sueruser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that support using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """Tag to be used for a recipe"""
    # задаем поле с названием
    name = models.CharField(max_length=255)
    # устанавливаем владельца
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient to be used in a recipe"""
    # устанавливаем поле названия
    name = models.CharField(max_length=255)
    # Задаем владельца
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        #  каскеда значит при удалении бзера удалится и рецепт
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe to cook"""
    # задаем юзера
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    # добаляем поле для названия
    title = models.CharField(max_length=255)
    # поле для времени приготавления
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    # задаем ссылку на рецепт если она есть, или возвращает пустую строку
    link = models.CharField(max_length=255, blank=True)
    # задаем ссылку на ингридеенты позволяющюу подгрущать множество полей
    ingredients = models.ManyToManyField('Ingredient')
    # задаем ссылку на ингридеенты позволяющюу подгрущать множество тегов
    tags = models.ManyToManyField('Tag')
    # добавляем поле изображения котрое может быть пустым
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title
