from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps
from .models import UserProfile, ProjectAccess


def user_permission_required(permission_name):
    """
    Декоратор для проверки конкретного права пользователя
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                if user_profile.has_permission(permission_name):
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, f'У вас нет прав для выполнения этого действия: {permission_name}')
                    return redirect('index')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Профиль пользователя не найден')
                return redirect('index')
        
        return _wrapped_view
    return decorator


def project_access_required(access_type='view'):
    """
    Декоратор для проверки доступа к проекту
    access_type: 'view', 'edit', 'delete'
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            project_id = kwargs.get('project_id') or request.POST.get('project_id') or request.GET.get('project_id')
            
            if not project_id:
                messages.error(request, 'ID проекта не указан')
                return redirect('index')
            
            try:
                # Проверяем общие права пользователя
                user_profile = UserProfile.objects.get(user=request.user)
                
                if access_type == 'view' and user_profile.can_view_projects:
                    return view_func(request, *args, **kwargs)
                elif access_type == 'edit' and user_profile.can_edit_projects:
                    return view_func(request, *args, **kwargs)
                elif access_type == 'delete' and user_profile.can_delete_projects:
                    return view_func(request, *args, **kwargs)
                
                # Проверяем специальные права доступа к проекту
                try:
                    project_access = ProjectAccess.objects.get(
                        user=request.user,
                        project_id=project_id
                    )
                    
                    if access_type == 'view' and project_access.can_view:
                        return view_func(request, *args, **kwargs)
                    elif access_type == 'edit' and project_access.can_edit:
                        return view_func(request, *args, **kwargs)
                    elif access_type == 'delete' and project_access.can_delete:
                        return view_func(request, *args, **kwargs)
                except ProjectAccess.DoesNotExist:
                    pass
                
                messages.error(request, f'У вас нет прав для {access_type} этого проекта')
                return redirect('index')
                
            except UserProfile.DoesNotExist:
                messages.error(request, 'Профиль пользователя не найден')
                return redirect('index')
        
        return _wrapped_view
    return decorator


def staff_permission_required(permission_type='view'):
    """
    Декоратор для проверки прав на работу с сотрудниками
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                
                if permission_type == 'view' and user_profile.can_view_staff:
                    return view_func(request, *args, **kwargs)
                elif permission_type == 'edit' and user_profile.can_edit_staff:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, f'У вас нет прав для {permission_type} сотрудников')
                    return redirect('index')
                    
            except UserProfile.DoesNotExist:
                messages.error(request, 'Профиль пользователя не найден')
                return redirect('index')
        
        return _wrapped_view
    return decorator


def customer_permission_required(permission_type='view'):
    """
    Декоратор для проверки прав на работу с заказчиками
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                
                if permission_type == 'view' and user_profile.can_view_customers:
                    return view_func(request, *args, **kwargs)
                elif permission_type == 'edit' and user_profile.can_edit_customers:
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, f'У вас нет прав для {permission_type} заказчиков')
                    return redirect('index')
                    
            except UserProfile.DoesNotExist:
                messages.error(request, 'Профиль пользователя не найден')
                return redirect('index')
        
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """
    Декоратор для проверки прав администратора
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                if not user_profile.can_manage_users:
                    messages.error(request, 'У вас нет прав администратора')
                    return redirect('index')
            except UserProfile.DoesNotExist:
                messages.error(request, 'Профиль пользователя не найден')
                return redirect('index')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def reports_access_required(view_func):
    """
    Декоратор для проверки прав на просмотр отчетов
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if not user_profile.can_view_reports:
                messages.error(request, 'У вас нет прав для просмотра отчетов')
                return redirect('index')
        except UserProfile.DoesNotExist:
            messages.error(request, 'Профиль пользователя не найден')
            return redirect('index')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

