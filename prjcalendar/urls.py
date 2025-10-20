from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from prjcalendar.customer import create_customer, edit_customer, read_customer
from prjcalendar.project import create_projects, edit_projects, read_projects
from prjcalendar.staff import create_staff, edit_staff, read_staff


from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path('edit/', views.edit, name='edit'),
    path('calendar/', views.calendar_tasks, name='calendar_tasks'),

    # Новые маршруты с проверкой прав доступа
    path('projects/', views.project_list, name='project_list'),
    path('projects/edit/<int:project_id>/',
         views.project_edit, name='project_edit'),
    path('staff/', views.staff_list, name='staff_list'),
    path('customers/', views.customer_list, name='customer_list'),
    path('reports/', views.reports, name='reports'),
    path('users/', views.user_management, name='user_management'),

    # ____________________________________________
    path('read_staff/', read_staff, name='read staff base'),
    path('staff/create/', create_staff, name='add staff to base'),
    path('staff/edit/<int:staff_id>/', edit_staff, name='edit staff in base'),
    # ____________________________________________
    path('read_customer/', read_customer, name='read customer base'),
    path('customer/create/', create_customer, name='add customer to base'),
    path('customer/edit/<int:customer_id>/',
         edit_customer, name='edit customer in base'),
    # ____________________________________________
    path('read_projects/', read_projects, name='read projects base'),
    path('projects/create/', create_projects, name='add projects to base'),
    path('projects/edit/<int:projects_id>/',
         edit_projects, name='edit projects in base'),

    # API для задач календаря
    path('api/save-task/', views.save_task, name='save_task'),
    path('api/load-tasks/', views.load_tasks, name='load_tasks'),
    path('api/delete-task/', views.delete_task, name='delete_task'),

    # API для работы с календарем
    path('api/save-calendar/', views.save_calendar_data, name='save_calendar_data'),
    path('api/load-calendar/', views.load_calendar_data, name='load_calendar_data'),
    path('api/update-project-color/', views.update_project_color,
         name='update_project_color'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
