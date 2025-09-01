from django.http import HttpResponseRedirect
from django.shortcuts import render
from prjcalendar.forms import StaffRoleForm
from prjcalendar.models import Customer, Project, Staff, StaffRole
from users import views as user_views
# import users

# Create your views here.


def index(request):
    '''Выводим журнал категорий
    '''
# def my_view(request):
    if request.user.is_authenticated:
        print(f'Юзер авторизован {request.user.username}')
        # return HttpResponse("Добро пожаловать обратно!")
    else:
        print(f'Юзер неавторизован {request.user.username}')
        return HttpResponseRedirect("/login/")
        # return render(request, 'login/')
        # return HttpResponse("Пожалуйста, авторизуйтесь.")
    # users = Users.objects.all()
    return render(request, "prjcalendar/users.html", context={"users": user_views, "title": "Пользователи"})


def edit(request):
    ''' тестим двигающиеся блоки '''
    # customer = Customer.objects.all()
    project = Project.objects.all()
    staff = Staff.objects.all()
    days = []
    for i in range(0,31):
        days.append(i)
    
    return render(request, "prjcalendar/div_move.html", context={'days': days, 'staff':staff, 'project': project, "title": "DIV move new"})

# class StaffCreateView(CreateView):
#     model = StaffRole
#     form_class = StaffRoleForm