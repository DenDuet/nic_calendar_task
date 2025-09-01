from datetime import datetime
# from django.forms import Form
from django.http import HttpResponsePermanentRedirect, HttpResponse
from django.shortcuts import render
from calendar.models import Recipe, Category, Journal
from django.core.files.storage import FileSystemStorage

from users.models import Profile
from .forms import RecipeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.views import login, logout

import logging

logger = logging.getLogger(__name__)


def logoutUser(request):
    '''
    Выход пользователя из системы
    '''
    logout(request)
    return redirect('login')


@login_required
def index(request):
    '''Стартовая страница
    '''
    users = Profile.objects.all()
    logger.info('Index page accessed')
    print(f"request.user.is_authenticated = {request.user.is_authenticated}, request.user.username = {request.user.username}")
    print(f"users = {users}")
    user = authenticate(username=request.username, password=request.password)
    if user is not None:
        if user.is_active:
            login(request, user)
            print(f"Авторизован = {user.username}")
            return render(request, "calendar/users.html", context={"users": users, "title": "Главная страница"})
            # Redirect to a success page.
        else:
            # Return a 'disabled account' error message
            ...    
            return HttpResponse("Пожалуйста, авторизуйтесь.")    
    
    # if request.user.is_authenticated:
    #     return render(request, "calendar/users.html", context={"users": users, "title": "Главная страница"})
    #     # return HttpResponse("Добро пожаловать обратно!")
    # else:
    #     return HttpResponse("Пожалуйста, авторизуйтесь.")    
    



def main_recipe(request, cat_id: int):
    '''Журнал рецептов с выбором по категориям
    '''

    rcps = Journal.objects.filter(category=cat_id)
    cats = Category.objects.all()
    cat = Category.objects.get(pk=cat_id)
    rcp = Recipe.objects.all().count
    data = datetime.now()
    # print(len(rcps))
    # len(rcps)
    logger.info(f'Распечатали список рецептов: {rcps}')
    return render(request, "calendar/main_recipe.html", context={'date': data, 'count': rcp, 'cat': cat, 'cats': cats, "recipe": rcps, "title": "Рецепты по категориям"})

# _________________CATEGORY______________________


def read_users(request):
    '''Выводим журнал категорий
    '''

    # users = User.objects.all()
    return render(request, "calendar/user.html", context={"users": users, "title": "Пользователи"})


@login_required
def create_category(request):
    '''Создаем категорию
    '''

    if request.method == 'POST':
        if request.POST.get('category_name') != "":
            category_name = " ".join(request.POST.get("category_name").split())
        if request.POST.get('description') != "":
            description = request.POST.get("description")

        cat = Category(category_name=category_name, description=description)
        cat.save()

        logger.info(f'Успешно создали новую категорию: {cat}.')
        cat = Category.objects.all()
        return render(request, "recipe/category.html", context={"category": cat, "title": "Категории"})
    else:
        logger.info(f'Создаем новую категорию.')

        return render(request, 'recipe/category_create.html', {"title": "Создаем категорию"})


@login_required
def edit_category(request, cat_id):
    '''Редактируем категорию и сохраняем
    '''

    if request.method == 'POST':
        cat = Category.objects.get(pk=cat_id)
        if request.POST.get('category_name') != "":
            cat.category_name = " ".join(
                request.POST.get("category_name").split())
        if request.POST.get('description') != "":
            cat.description = request.POST.get("description")

        # created = Category.objects.update_or_create(
        #     category_name=category_name, description=description)
        cat.save()
        logger.info(f'Успешно обновили категорию: {cat}.')
        cat = Category.objects.all()
        return render(request, "recipe/category.html", context={"category": cat, "title": "Категории"})
    else:
        cat = Category.objects.get(pk=cat_id)
        logger.info(f'Редактируем категорию')

        return render(request, 'recipe/category_edit.html', {'cat': cat, "title": "Создаем категорию"})


@login_required
def delete_category(request, cat_id: int):
    '''Удаляем категорию
    '''

    cat = Category.objects.get(pk=cat_id)
    cat.delete()
    cat = Category.objects.all()
    # print(name)
    logger.info(f'Удалили категорию. Автор - {request.user}')
    return render(request, "recipe/category.html", context={"category": cat, "title": "Категории"})
# _________________CATEGORY______________________


# _________________RECIPE______________________

def read_recipe(request):
    '''Выводим все рецепты в таблице
    '''

    recipe = Recipe.objects.all()
    # print(name)
    logger.info(f'Распечатали список рецептов: {recipe}')
    return render(request, "recipe/recipe.html", context={"recipe": recipe, "title": "Рецепты"})


def upload_image(image, recipe_id):
    '''Загружаем картинку рецепта
    '''

    fs = FileSystemStorage()
    filename = fs.save(image.name, image)
    file_url = fs.url(filename)
    cat = Recipe.objects.get(pk=recipe_id)
    cat.image = file_url
    cat.save()
    return file_url


@login_required
def create_recipe(request):
    '''Создаем новый рецепт и сохраняем
    '''

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)

        if request.POST.get('name') != "":
            name = " ".join(request.POST.get("name").split())
        if request.POST.get('make_time') != "":
            make_time = " ".join(request.POST.get("make_time").split())
        if request.POST.get('description') != "":
            description = request.POST.get("description")
        if request.POST.get('steps') != "":
            steps = request.POST.get("steps")
        if request.POST.get('ingredients') != "":
            ingredients = request.POST.get("ingredients")
        recipe = Recipe(name=name, description=description, make_time=make_time,
                        steps=steps, ingredients=ingredients, author=request.user)
        recipe.save()

        file_ = request.FILES.get("image", None)
        if file_ != None:
            file = request.FILES['image']
            upload_image(file, recipe.id)
        logger.info(f'Успешно создали рецепт: {recipe}.')
        recipe = Recipe.objects.all()
        return render(request, "recipe/recipe.html", context={"recipe": recipe, "title": "Рецепты"})

    else:
        form = RecipeForm()
        cat = Category.objects.order_by('category_name')

    return render(request, 'recipe/recipe_create.html', {'cat': cat, 'form': form, "title": "Создаем рецепт"})


@login_required
def edit_recipe(request, rcp_id: int):
    '''Редактируем рецепт и обновляем запись '''

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        recipe = Recipe.objects.get(pk=rcp_id)
        if request.POST.get('name') != "":
            recipe.name = " ".join(request.POST.get("name").split())
        if request.POST.get('make_time') != "":
            recipe.make_time = " ".join(request.POST.get("make_time").split())
        if request.POST.get('description') != "":
            recipe.description = request.POST.get("description")
        if request.POST.get('steps') != "":
            recipe.steps = request.POST.get("steps")
        if request.POST.get('ingredients') != "":
            recipe.ingredients = request.POST.get("ingredients")
        recipe.save()
        file_ = request.FILES.get("image", None)
        if file_ != None:
            file = request.FILES['image']
            upload_image(file, recipe.id)
        print(f"file_ = {file_}, recipe.image = {recipe.image} ")
        logger.info(f'Успешно обновили рецепт: {recipe}.')
        recipe = Recipe.objects.get(pk=rcp_id)

        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

    else:
        form = RecipeForm()
        cat = Category.objects.order_by('category_name')
        recipe = Recipe.objects.get(pk=rcp_id)
        journal = Journal.objects.filter(recipe_name=recipe)

    return render(request, 'recipe/recipe_edit.html', {'journal': journal, 'category': cat, 'recipe': recipe, 'form': form, "title": "Редактируем рецепт"})


@login_required
def delete_recipe(request, rcp_id: int):
    '''Удаляем рецепт из базы'''

    rcp = Recipe.objects.get(pk=rcp_id)
    rcp.delete()
    name = Recipe.objects.all()
    # print(name)
    logger.info(f'Удалили рецепт. Автор - {request.user}')
    return render(request, "recipe/recipe.html", context={"recipe": name, "title": "Рецепты"})
# _________________RECIPE______________________


@login_required
def create_jrn(request, rcp_id: int):
    '''Создаем запись в журнале принадлежности рецепта к категории
        это делается из редактора рецепта'''

    path_url = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        if request.POST.get('name') != "":
            name = request.POST.get("name")
        if request.POST.get('cat') != "":
            cat = request.POST.get("cat")
        path_url = request.POST.get("path_url")
        rcp = Recipe.objects.get(name=name)
        cat = Category.objects.get(category_name=cat)

        jrn = Journal.objects.update_or_create(recipe_name=rcp, category=cat)

        logger.info(f'Успешно создали этап проекта: {jrn}.')
        return HttpResponsePermanentRedirect(path_url)

    else:
        cat = Category.objects.all()
        recipe = Recipe.objects.get(pk=rcp_id)
        return render(request, "recipe/journal_create.html", context={'path_url': path_url, 'recipe': recipe, "category": cat, "title": "Рецепты"})


@login_required
def delete_jrn(request, jrn_id: int):
    '''Удаляем запись в журнале принадлежности рецепта к категории
        это делается из редактора рецепта'''

    stage = Journal.objects.get(pk=jrn_id)
    stage.delete()
    logger.info(f'Успешно удалили этап проекта.')
    return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


@login_required
def edit_jrn(request, rcp_id: int, cat_id: int):
    '''Редактируем запись в журнале принадлежности рецепта к категории
        Редактируется это в редакторе рецепта'''

    path_url = request.META.get('HTTP_REFERER')
    # print(f'Адрес страницы: {path_url}')
    if request.method == 'POST':
        if request.POST.get('name') != "":
            name = request.POST.get("name")
        if request.POST.get('cat') != "":
            cat = request.POST.get("cat")
        path_url = request.POST.get("path_url")
        rcp = Recipe.objects.get(name=name)
        cat = Category.objects.get(category_name=cat)

        jrn = Journal.objects.update_or_create(recipe_name=rcp, category=cat)

        logger.info(f'Успешно обновили этап проекта: {jrn}.')

        return HttpResponsePermanentRedirect(path_url)

    else:
        cat = Category.objects.get(pk=cat_id)
        recipe = Recipe.objects.get(pk=rcp_id)
    return render(request, "recipe/journal_edit.html", context={'path_url': path_url, 'recipe': recipe, "category": cat, "title": "Рецепты"})
