from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import UserProfile, UserGroup, ProjectAccess, Project, Staff, Customer


def create_default_groups():
    """Создает стандартные группы пользователей с правами доступа"""

    # Группа администраторов
    admin_group, created = UserGroup.objects.get_or_create(
        name="Администраторы",
        defaults={
            'description': 'Полный доступ ко всем функциям системы'
        }
    )

    # Группа менеджеров
    manager_group, created = UserGroup.objects.get_or_create(
        name="Менеджеры",
        defaults={
            'description': 'Управление проектами, сотрудниками и заказчиками'
        }
    )

    # Группа сотрудников
    staff_group, created = UserGroup.objects.get_or_create(
        name="Сотрудники",
        defaults={
            'description': 'Просмотр проектов и отчетов, редактирование своих данных'
        }
    )

    # Группа наблюдателей
    viewer_group, created = UserGroup.objects.get_or_create(
        name="Наблюдатели",
        defaults={
            'description': 'Только просмотр проектов и отчетов'
        }
    )

    return {
        'admin': admin_group,
        'manager': manager_group,
        'staff': staff_group,
        'viewer': viewer_group
    }


def setup_default_permissions():
    """Настраивает стандартные права для групп"""

    groups = create_default_groups()

    # Права для администраторов
    admin_profile = UserProfile.objects.filter(
        user_group=groups['admin']).first()
    if admin_profile:
        admin_profile.can_view_projects = True
        admin_profile.can_edit_projects = True
        admin_profile.can_delete_projects = True
        admin_profile.can_view_staff = True
        admin_profile.can_edit_staff = True
        admin_profile.can_view_customers = True
        admin_profile.can_edit_customers = True
        admin_profile.can_manage_users = True
        admin_profile.can_view_reports = True
        admin_profile.save()

    # Права для менеджеров
    manager_profile = UserProfile.objects.filter(
        user_group=groups['manager']).first()
    if manager_profile:
        manager_profile.can_view_projects = True
        manager_profile.can_edit_projects = True
        manager_profile.can_delete_projects = False
        manager_profile.can_view_staff = True
        manager_profile.can_edit_staff = True
        manager_profile.can_view_customers = True
        manager_profile.can_edit_customers = True
        manager_profile.can_manage_users = False
        manager_profile.can_view_reports = True
        manager_profile.save()

    # Права для сотрудников
    staff_profile = UserProfile.objects.filter(
        user_group=groups['staff']).first()
    if staff_profile:
        staff_profile.can_view_projects = True
        staff_profile.can_edit_projects = False
        staff_profile.can_delete_projects = False
        staff_profile.can_view_staff = True
        staff_profile.can_edit_staff = False
        staff_profile.can_view_customers = True
        staff_profile.can_edit_customers = False
        staff_profile.can_manage_users = False
        staff_profile.can_view_reports = True
        staff_profile.save()

    # Права для наблюдателей
    viewer_profile = UserProfile.objects.filter(
        user_group=groups['viewer']).first()
    if viewer_profile:
        viewer_profile.can_view_projects = True
        viewer_profile.can_edit_projects = False
        viewer_profile.can_delete_projects = False
        viewer_profile.can_view_staff = True
        viewer_profile.can_edit_staff = False
        viewer_profile.can_view_customers = True
        viewer_profile.can_edit_customers = False
        viewer_profile.can_manage_users = False
        viewer_profile.can_view_reports = True
        viewer_profile.save()


def assign_user_to_group(user, group_name):
    """Назначает пользователя в группу и создает профиль с правами"""

    try:
        group = UserGroup.objects.get(name=group_name)

        # Создаем или обновляем профиль пользователя
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'user_group': group}
        )

        if not created:
            profile.user_group = group
            profile.save()

        # Применяем права группы
        apply_group_permissions(profile, group)

        return True, f"Пользователь {user.username} успешно назначен в группу {group_name}"

    except UserGroup.DoesNotExist:
        return False, f"Группа {group_name} не найдена"


def apply_group_permissions(profile, group):
    """Применяет права группы к профилю пользователя"""

    if group.name == "Администраторы":
        profile.can_view_projects = True
        profile.can_edit_projects = True
        profile.can_delete_projects = True
        profile.can_view_staff = True
        profile.can_edit_staff = True
        profile.can_view_customers = True
        profile.can_edit_customers = True
        profile.can_manage_users = True
        profile.can_view_reports = True

    elif group.name == "Менеджеры":
        profile.can_view_projects = True
        profile.can_edit_projects = True
        profile.can_delete_projects = False
        profile.can_view_staff = True
        profile.can_edit_staff = True
        profile.can_view_customers = True
        profile.can_edit_customers = True
        profile.can_manage_users = False
        profile.can_view_reports = True

    elif group.name == "Сотрудники":
        profile.can_view_projects = True
        profile.can_edit_projects = False
        profile.can_delete_projects = False
        profile.can_view_staff = True
        profile.can_edit_staff = False
        profile.can_view_customers = True
        profile.can_edit_customers = False
        profile.can_manage_users = False
        profile.can_view_reports = True

    elif group.name == "Наблюдатели":
        profile.can_view_projects = True
        profile.can_edit_projects = False
        profile.can_delete_projects = False
        profile.can_view_staff = True
        profile.can_edit_staff = False
        profile.can_view_customers = True
        profile.can_edit_customers = False
        profile.can_manage_users = False
        profile.can_view_reports = True

    profile.save()


def get_user_permissions(user):
    """Возвращает все права пользователя"""

    try:
        profile = UserProfile.objects.get(user=user)
        return {
            'can_view_projects': profile.can_view_projects,
            'can_edit_projects': profile.can_edit_projects,
            'can_delete_projects': profile.can_delete_projects,
            'can_view_staff': profile.can_view_staff,
            'can_edit_staff': profile.can_edit_staff,
            'can_view_customers': profile.can_view_customers,
            'can_edit_customers': profile.can_edit_customers,
            'can_manage_users': profile.can_manage_users,
            'can_view_reports': profile.can_view_reports,
            'group': profile.user_group.name if profile.user_group else None
        }
    except UserProfile.DoesNotExist:
        return None


def check_project_access(user, project_id, access_type='view'):
    """Проверяет доступ пользователя к проекту"""

    try:
        profile = UserProfile.objects.get(user=user)

        # Проверяем общие права
        if access_type == 'view' and profile.can_view_projects:
            return True
        elif access_type == 'edit' and profile.can_edit_projects:
            return True
        elif access_type == 'delete' and profile.can_delete_projects:
            return True

        # Проверяем специальные права доступа к проекту
        try:
            project_access = ProjectAccess.objects.get(
                user=user,
                project_id=project_id
            )

            if access_type == 'view' and project_access.can_view:
                return True
            elif access_type == 'edit' and project_access.can_edit:
                return True
            elif access_type == 'delete' and project_access.can_delete:
                return True
        except ProjectAccess.DoesNotExist:
            pass

        return False

    except UserProfile.DoesNotExist:
        return False


def get_accessible_projects(user):
    """Возвращает список проектов, доступных пользователю"""

    try:
        profile = UserProfile.objects.get(user=user)

        if profile.can_view_projects:
            # Если у пользователя есть общие права на просмотр проектов
            projects = Project.objects.filter(isDeleted=False)

            # Добавляем проекты с специальным доступом
            special_access_ids = list(ProjectAccess.objects.filter(
                user=user,
                can_view=True
            ).values_list('project_id', flat=True))

            if special_access_ids:
                special_projects = Project.objects.filter(
                    id__in=special_access_ids, isDeleted=False)
                projects = projects | special_projects

            return projects.distinct()

        else:
            # Только проекты с специальным доступом
            special_access_ids = list(ProjectAccess.objects.filter(
                user=user,
                can_view=True
            ).values_list('project_id', flat=True))

            if special_access_ids:
                return Project.objects.filter(id__in=special_access_ids, isDeleted=False)
            else:
                return Project.objects.none()

    except UserProfile.DoesNotExist:
        return Project.objects.none()
    except Exception as e:
        # Логируем ошибку для отладки
        import logging
        logger = logging.getLogger(__name__)
        logger.error(
            "Ошибка в get_accessible_projects для пользователя %s: %s", user.username, str(e))
        return Project.objects.none()


def create_user_profile_for_existing_users():
    """Создает профили для существующих пользователей"""

    users_without_profile = User.objects.filter(
        userprofile__isnull=True
    )

    for user in users_without_profile:
        # По умолчанию назначаем в группу "Наблюдатели"
        assign_user_to_group(user, "Наблюдатели")

    return len(users_without_profile)
