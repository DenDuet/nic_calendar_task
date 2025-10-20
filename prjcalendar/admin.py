from django.contrib import admin
from .models import (
    StaffRole, Progress, Customer, Staff, Project, Staff_prj,
    UserGroup, UserProfile, ProjectAccess, Task
)

# Register your models here.


@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    filter_horizontal = ['permissions']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'user_group', 'staff_member', 'can_view_projects',
        'can_edit_projects', 'can_view_staff', 'can_edit_staff',
        'can_manage_users', 'created_at'
    ]
    list_filter = [
        'user_group', 'can_view_projects', 'can_edit_projects',
        'can_view_staff', 'can_edit_staff', 'can_manage_users',
        'created_at'
    ]
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    ordering = ['user__username']
    raw_id_fields = ['user', 'staff_member']


@admin.register(ProjectAccess)
class ProjectAccessAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'project', 'can_view', 'can_edit', 'can_delete',
        'granted_by', 'granted_at'
    ]
    list_filter = ['can_view', 'can_edit', 'can_delete', 'granted_at']
    search_fields = ['user__username', 'project__name_prj']
    ordering = ['-granted_at']
    raw_id_fields = ['user', 'project', 'granted_by']


@admin.register(StaffRole)
class StaffRoleAdmin(admin.ModelAdmin):
    list_display = ['name_staffrole']
    search_fields = ['name_staffrole']
    ordering = ['name_staffrole']


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['name_progress']
    search_fields = ['name_progress']
    ordering = ['name_progress']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name_firm', 'name_contact', 'phone', 'email', 'isDeleted']
    list_filter = ['isDeleted']
    search_fields = ['name_firm', 'name_contact', 'phone', 'email']
    ordering = ['name_firm']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = [
        'name_family', 'name_first', 'name_second', 'roleID',
        'phone', 'email', 'isPrj', 'isDeleted'
    ]
    list_filter = ['roleID', 'isPrj', 'isDeleted']
    search_fields = ['name_family', 'name_first',
                     'name_second', 'phone', 'email']
    ordering = ['name_family', 'name_first']
    raw_id_fields = ['roleID']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'name_prj', 'date_start', 'date_finish', 'contact_customer',
        'sum_prj', 'progress', 'isDeleted'
    ]
    list_filter = ['progress', 'isDeleted', 'date_start', 'date_finish']
    search_fields = ['name_prj', 'contact_customer__name_firm']
    ordering = ['-date_start']
    raw_id_fields = ['contact_customer', 'progress']
    date_hierarchy = 'date_start'


@admin.register(Staff_prj)
class StaffPrjAdmin(admin.ModelAdmin):
    list_display = ['staffID', 'prjID', 'date_work', 'work']
    list_filter = ['date_work', 'staffID', 'prjID']
    search_fields = ['work', 'staffID__name_family', 'prjID__name_prj']
    ordering = ['-date_work']
    raw_id_fields = ['staffID', 'prjID']
    date_hierarchy = 'date_work'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'staff', 'day', 'duration',
                    'color', 'project', 'created_by', 'created_at']
    list_filter = ['staff', 'day', 'project',
                   'created_by', 'created_at', 'is_deleted']
    search_fields = ['name', 'staff__name_family',
                     'staff__name_first', 'project__name_prj']
    list_editable = ['day', 'duration', 'color']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'staff', 'day', 'duration', 'color', 'project')
        }),
        ('Системная информация', {
            'fields': ('created_by', 'created_at', 'updated_at', 'is_deleted'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Если это новая задача
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
