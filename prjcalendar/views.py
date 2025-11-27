from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from prjcalendar.forms import StaffRoleForm
from prjcalendar.models import Customer, Project, Staff, StaffRole
from prjcalendar.decorators import (
    user_permission_required,
    project_access_required,
    staff_permission_required,
    customer_permission_required,
    admin_required,
    reports_access_required
)
from prjcalendar.permissions import get_user_permissions, get_accessible_projects
from users import views as user_views
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from prjcalendar.models import Task
import json
from django.shortcuts import get_object_or_404

# Create your views here.


@login_required
def index(request):
    '''Выводим журнал категорий'''
    try:
        if request.user.is_authenticated:
            print(f'Юзер авторизован {request.user.username}')

            # Проверяем наличие UserProfile, создаем если нет
            from prjcalendar.models import UserProfile, UserGroup
            try:
                UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                # Создаем профиль пользователя с правами по умолчанию
                try:
                    from prjcalendar.permissions import assign_user_to_group, create_default_groups
                    # Убеждаемся, что группы существуют
                    create_default_groups()
                    assign_user_to_group(request.user, "Наблюдатели")
                    print(
                        f'Создан профиль для пользователя {request.user.username}')
                except Exception as e:
                    # Если не удалось создать через группу, создаем базовый профиль
                    print(f'Ошибка при создании профиля через группу: {e}')
                    default_group = UserGroup.objects.first()
                    if not default_group:
                        from prjcalendar.permissions import create_default_groups
                        create_default_groups()
                        default_group = UserGroup.objects.first()

                    UserProfile.objects.create(
                        user=request.user,
                        user_group=default_group,
                        can_view_projects=True,
                        can_view_staff=True,
                        can_view_customers=True,
                        can_view_reports=True
                    )
                    print(
                        f'Создан базовый профиль для пользователя {request.user.username}')

            # Получаем права пользователя для отображения в интерфейсе
            user_permissions = get_user_permissions(request.user)

            # Получаем доступные проекты
            accessible_projects = get_accessible_projects(request.user)

            context = {
                "users": user_views,
                "title": "Пользователи",
                "user_permissions": user_permissions,
                "accessible_projects": accessible_projects
            }
        else:
            print(f'Юзер неавторизован {request.user.username}')
            return HttpResponseRedirect("/login/")

        return render(request, "prjcalendar/users.html", context=context)
    except Exception as e:
        # Логируем ошибку для отладки
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        logger.error("Ошибка в index view: %s\n%s", error_msg, traceback_str)

        # Возвращаем простую страницу с ошибкой или редирект
        messages.error(
            request, 'Произошла ошибка при загрузке страницы. Пожалуйста, обратитесь к администратору.')
        return render(request, "prjcalendar/users.html", context={
            "title": "Ошибка",
            "user_permissions": None,
            "accessible_projects": []
        })


@login_required
@user_permission_required('can_view_projects')
def edit(request):
    ''' тестим двигающиеся блоки '''
    # Получаем только доступные проекты
    accessible_projects = get_accessible_projects(request.user)
    staff = Staff.objects.all()
    days = []
    for i in range(0, 31):
        days.append(i)

    return render(request, "prjcalendar/div_move.html", context={
        'days': days,
        'staff': staff,
        'project': accessible_projects,
        "title": "DIV move new"
    })


@login_required
@user_permission_required('can_view_projects')
def project_list(request):
    """Список проектов с учетом прав доступа"""
    accessible_projects = get_accessible_projects(request.user)

    context = {
        'projects': accessible_projects,
        'title': 'Список проектов'
    }
    return render(request, "prjcalendar/project_list.html", context=context)


@login_required
@project_access_required('edit')
def project_edit(request, project_id):
    """Редактирование проекта"""
    try:
        project = Project.objects.get(id=project_id, isDeleted=False)
        context = {
            'project': project,
            'title': f'Редактирование проекта: {project.name_prj}'
        }
        return render(request, "prjcalendar/project_edit.html", context=context)
    except Project.DoesNotExist:
        messages.error(request, 'Проект не найден')
        return redirect('project_list')


@login_required
@staff_permission_required('view')
def staff_list(request):
    """Список сотрудников"""
    staff_members = Staff.objects.filter(isDeleted=False)

    context = {
        'staff_members': staff_members,
        'title': 'Список сотрудников'
    }
    return render(request, "prjcalendar/staff_list.html", context=context)


@login_required
@customer_permission_required('view')
def customer_list(request):
    """Список заказчиков"""
    customers = Customer.objects.filter(isDeleted=False)

    context = {
        'customers': customers,
        'title': 'Список заказчиков'
    }
    return render(request, "prjcalendar/customer_list.html", context=context)


@login_required
@reports_access_required
def reports(request):
    """Отчеты"""
    context = {
        'title': 'Отчеты'
    }
    return render(request, "prjcalendar/reports.html", context=context)


@login_required
@admin_required
def user_management(request):
    """Управление пользователями"""
    from django.contrib.auth.models import User
    from prjcalendar.models import UserProfile, UserGroup

    users = User.objects.all()
    user_profiles = UserProfile.objects.all()
    user_groups = UserGroup.objects.all()

    context = {
        'users': users,
        'user_profiles': user_profiles,
        'user_groups': user_groups,
        'title': 'Управление пользователями'
    }
    return render(request, "prjcalendar/user_management.html", context=context)


@login_required
@user_permission_required('can_view_projects')
def calendar_tasks(request):
    ''' Улучшенный календарь с задачами '''
    # Получаем только доступные проекты
    accessible_projects = get_accessible_projects(request.user)

    # Получаем всех сотрудников (убираем фильтр isPrj=True)
    staff = Staff.objects.filter(isDeleted=False)

    # Если сотрудников нет, создаем тестовые данные
    if not staff.exists():
        print("ВНИМАНИЕ: Сотрудники не найдены! Создаем тестовые данные...")
        # Создаем тестового сотрудника если их нет
        from prjcalendar.models import StaffRole
        try:
            default_role = StaffRole.objects.first()
            if not default_role:
                default_role = StaffRole.objects.create(
                    name_staffrole="Тестовая роль")

            staff = Staff.objects.create(
                name_family="Тестовый",
                name_first="Сотрудник",
                roleID=default_role,
                isDeleted=False
            )
            staff = Staff.objects.filter(isDeleted=False)
        except Exception as e:
            print(f"Ошибка создания тестового сотрудника: {e}")

    days = []
    for i in range(1, 32):  # Дни месяца от 1 до 31
        days.append(i)

    # Отладочная информация
    print(f"DEBUG: Проектов найдено: {accessible_projects.count()}")
    print(f"DEBUG: Сотрудников найдено: {staff.count()}")
    print(f"DEBUG: Дней: {len(days)}")

    # Выводим информацию о сотрудниках
    for s in staff:
        print(f"DEBUG: Сотрудник {s.id}: {s.name_family} {s.name_first}")

    context = {
        'days': days,
        'staff': staff,
        'project': accessible_projects,
        "title": "Календарь задач"
    }
    return render(request, "prjcalendar/calendar_tasks.html", context=context)

# class StaffCreateView(CreateView):
#     model = StaffRole
#     form_class = StaffRoleForm

# API для задач календаря


@csrf_exempt
@login_required
def save_task(request):
    """API для сохранения задачи в базе данных"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Получаем или создаем задачу
            task_id = data.get('id')
            if task_id and task_id.startswith('task_'):
                # Это новая задача из localStorage
                task = None
            else:
                # Это существующая задача
                task = Task.objects.filter(id=task_id).first()

            if not task:
                task = Task()

            # Обновляем данные задачи
            task.name = data.get('name', '')
            task.staff = get_object_or_404(Staff, id=data.get('staffId'))
            task.day = data.get('day', 1)
            task.duration = data.get('duration', 1)
            task.color = data.get('color', '#007bff')

            # Связываем с проектом если есть
            project_id = data.get('projectId')
            if project_id:
                task.project = get_object_or_404(Project, id=project_id)

            # Устанавливаем создателя
            task.created_by = request.user

            task.save()

            return JsonResponse({
                'success': True,
                'task_id': task.id,
                'message': f'Задача "{task.name}" сохранена'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({'success': False, 'error': 'Только POST запросы'}, status=405)


@csrf_exempt
@login_required
def load_tasks(request):
    """API для загрузки задач из базы данных"""
    try:
        tasks = Task.objects.filter(
            is_deleted=False).select_related('staff', 'project')

        tasks_data = []
        for task in tasks:
            tasks_data.append({
                'id': f'task_{task.id}',
                'staffId': task.staff.id,
                'day': task.day,
                'name': task.name,
                'duration': task.duration,
                'color': task.color,
                'projectId': task.project.id if task.project else None,
                'created': task.created_at.isoformat()
            })

        return JsonResponse({
            'success': True,
            'tasks': tasks_data
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@login_required
def delete_task(request):
    """API для удаления задачи"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('id')

            if task_id and task_id.startswith('task_'):
                # Удаляем из localStorage
                return JsonResponse({'success': True, 'message': 'Задача удалена из localStorage'})

            # Удаляем из базы данных
            task = get_object_or_404(Task, id=task_id)
            task.is_deleted = True
            task.save()

            return JsonResponse({
                'success': True,
                'message': f'Задача "{task.name}" удалена'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({'success': False, 'error': 'Только POST запросы'}, status=405)


@csrf_exempt
@login_required
def save_calendar_data(request):
    """API для сохранения всех данных календаря в БД"""
    print(
        f"DEBUG: Запрос к save_calendar_data от пользователя {request.user.username}")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tasks = data.get('tasks', [])
            print(f"DEBUG: Получено {len(tasks)} задач для сохранения")
            saved_count = 0
            errors = []

            for task_data in tasks:
                try:
                    # Получаем или создаем задачу
                    task_id = task_data.get('id')
                    if task_id and task_id.startswith('task_'):
                        # Это новая задача из localStorage
                        task = Task()
                    else:
                        # Это существующая задача
                        task = Task.objects.filter(id=task_id).first()
                        if not task:
                            task = Task()

                    # Обновляем данные задачи
                    task.name = task_data.get('name', '')
                    task.staff = get_object_or_404(
                        Staff, id=task_data.get('staffId'))
                    task.day = task_data.get('day', 1)
                    task.duration = task_data.get('duration', 1)
                    task.color = task_data.get('color', '#007bff')

                    # Связываем с проектом если есть
                    project_id = task_data.get('projectId')
                    if project_id:
                        task.project = get_object_or_404(
                            Project, id=project_id)

                    # Устанавливаем создателя
                    task.created_by = request.user

                    task.save()
                    saved_count += 1
                    print(f"DEBUG: Сохранена задача: {task.name}")

                except Exception as e:
                    error_msg = f"Ошибка сохранения задачи {task_data.get('name', 'Без названия')}: {str(e)}"
                    errors.append(error_msg)
                    print(f"DEBUG: {error_msg}")

            print(
                f"DEBUG: Успешно сохранено {saved_count} задач, ошибок: {len(errors)}")
            return JsonResponse({
                'success': True,
                'saved_count': saved_count,
                'errors': errors,
                'message': f'Сохранено {saved_count} задач'
            })

        except Exception as e:
            print(f"DEBUG: Ошибка в save_calendar_data: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({'success': False, 'error': 'Только POST запросы'}, status=405)


@csrf_exempt
@login_required
def load_calendar_data(request):
    """API для загрузки всех данных календаря из БД"""
    print(
        f"DEBUG: Запрос к load_calendar_data от пользователя {request.user.username}")
    try:
        # Загружаем задачи
        tasks = Task.objects.filter(
            is_deleted=False).select_related('staff', 'project')

        tasks_data = []
        for task in tasks:
            tasks_data.append({
                'id': f'task_{task.id}',
                'staffId': task.staff.id,
                'day': task.day,
                'name': task.name,
                'duration': task.duration,
                'color': task.color,
                'projectId': task.project.id if task.project else None,
                'created': task.created_at.isoformat()
            })

        # Загружаем проекты с цветами
        projects = get_accessible_projects(request.user)
        projects_data = []
        for project in projects:
            projects_data.append({
                'id': project.id,
                'name': project.name_prj,
                'color': project.color,
                'date_start': project.date_start.isoformat(),
                'date_finish': project.date_finish.isoformat(),
                'customer': project.contact_customer.name_firm if project.contact_customer else None
            })

        print(
            f"DEBUG: Найдено {len(tasks_data)} задач и {len(projects_data)} проектов")
        return JsonResponse({
            'success': True,
            'tasks': tasks_data,
            'projects': projects_data
        })

    except Exception as e:
        print(f"DEBUG: Ошибка в load_calendar_data: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@login_required
def update_project_color(request):
    """API для обновления цвета проекта"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            project_id = data.get('projectId')
            color = data.get('color', '#007bff')

            project = get_object_or_404(Project, id=project_id)
            project.color = color
            project.save()

            return JsonResponse({
                'success': True,
                'message': f'Цвет проекта "{project.name_prj}" обновлен'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({'success': False, 'error': 'Только POST запросы'}, status=405)
