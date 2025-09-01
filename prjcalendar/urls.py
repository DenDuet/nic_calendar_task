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
    # ____________________________________________
    path('read_staff/', read_staff, name='read staff base'),
    path('staff/create/', create_staff, name='add staff to base'),
    path('staff/edit/<int:staff_id>/', edit_staff, name='edit staff in base'),
    # ____________________________________________

    path('read_customer/', read_customer, name='read customer base'),
    path('customer/create/', create_customer, name='add customer to base'),
    path('customer/edit/<int:customer_id>/', edit_customer, name='edit customer in base'),
    # ____________________________________________
    path('read_projects/', read_projects, name='read projects base'),
    path('projects/create/', create_projects, name='add projects to base'),
    path('projects/edit/<int:projects_id>/', edit_projects, name='edit projects in base'),
  
    # ____________________________________________
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)