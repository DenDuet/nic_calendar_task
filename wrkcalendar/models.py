from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
# from django.core.management.base import BaseCommand

# Create your models here.


class Recipe(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=500, unique=False)
    steps = models.TextField(max_length=500, unique=False)
    add_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=settings.MEDIA_ROOT)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    ingredients = models.TextField(max_length=500, unique=False)
    make_time = models.CharField(max_length=50, unique=False)

    def __str__(self):
        return f'Рецепт: {self.name}'


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=250, unique=False)

    def __str__(self):
        return f'Категория: {self.category_name}'


class Journal(models.Model):
    recipe_name = models.ForeignKey(Recipe, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    date_reged = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.recipe_name.name}'
