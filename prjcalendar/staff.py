from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# from django.http import HttpResponsePermanentRedirect, JsonResponse

from .models import Staff, StaffRole
from .forms import StaffForm

import logging

logger = logging.getLogger(__name__)

# __________________Контантные лица_____________________________


@login_required
def read_staff(request):
    staff = Staff.objects.all()
    # print(staff)
    logger.info(f'Распечатали список контактных лиц: {staff}')
    return render(request, "prjcalendar/staff_table.html", context={"staff": staff, "title": "Сотрудники"})


@login_required
def create_staff(request):
    roles = StaffRole.objects.all()
    # print(f"roles = {roles}")
    if len(roles)==0:
        staffrole = StaffRole(name_staffrole="Директор")
        print(f"staffrole = {staffrole}")
        staffrole.save()
        

    if request.method == 'POST':
        # form = StaffForm(request.POST)    
        if request.POST.get('name_family') != "":
            name_family = " ".join(request.POST.get("name_family").split())
        else:
            name_family = ""
        if request.POST.get('name_first') != "":
            name_first = " ".join(request.POST.get("name_first").split())
        if request.POST.get('name_second') != "":
            name_second = " ".join(request.POST.get("name_second").split())
        else:
            name_second = ""
        if request.POST.get('roleID') != "":
            # print(f"request.POST.get('roleID') = {request.POST.get("roleID")}")
            roleID = StaffRole.objects.get(name_staffrole=request.POST.get("roleID"))
        if request.POST.get('birthday') != "":
            birthday = request.POST.get("birthday")
        else:
            birthday = ""
        if request.POST.get('phone') != "":
            phone = " ".join(request.POST.get("phone").split())
        if request.POST.get('email') != "":
            email = request.POST.get("email")
        else:
            email = ""
       
        staff = Staff(birthday=birthday, name_family=name_family, name_first=name_first, name_second=name_second, roleID=roleID, phone=phone, email=email)
        staff.save()
        staff = Staff.objects.all()
        return render(request, 'prjcalendar/staff_table.html', {"request": request, "staff": staff, "title": "Сотрудники"})

        # return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
    else:
        staff = Staff.objects.all()
        form = StaffForm({'staff': staff})
        # print(f"Пустая форма {staffs}")
    return render(request, 'prjcalendar/staff_new.html', {'roles': roles, 'staff': staff, 'form': form,  "title": "Сотрудники"})


@login_required
def edit_staff(request, staff_id: int):
    # staff = Staff.objects.get(pk=staff_id)
    if request.method == 'POST':
        # form = StaffForm(request.POST)
        staff = Staff.objects.get(pk=staff_id)
        if request.POST.get('name_family') != "":
            staff.name_family = " ".join(request.POST.get("name_family").split())
        if request.POST.get('name_first') != "":
            staff.name_first = " ".join(request.POST.get("name_first").split())
        if request.POST.get('name_second') != "":
            staff.name_second = " ".join(request.POST.get("name_second").split())
        if request.POST.get("roleID")!="":            
            name_staffrole = " ".join(request.POST.get("roleID").split())
            staff.roleID = StaffRole.objects.get(name_staffrole=name_staffrole)
         
        if request.POST.get('birthday') != "":
            staff.birthday = request.POST.get('birthday')
        if request.POST.get('phone') != "":
            staff.phone = " ".join(request.POST.get("phone").split())
        if request.POST.get('email') != "":
            staff.email = request.POST.get('email')

        staff.save()
        logger.info(f'Успешно обновили данные сотрудников: {staff_id}.')
        staff = Staff.objects.all()

        return render(request, "prjcalendar/staff_table.html", context={"staff": staff, "title": "Сотрудники"})

    else:
        staff = Staff.objects.get(pk=staff_id)
        roles = StaffRole.objects.all()

    return render(request, 'prjcalendar/staff_edit.html', {'staff': staff, 'roles': roles, "title": "Сотрудники"})

# ______________заполнение служебных спрвочников_______________________

@login_required
def read_staffrole(request, todo):
    # if todo == 'delete':
    #     staffrole = StaffRole.objects.get(pk=el_id)
    #     print(f'{staffrole}')
    #     staffrole.delete()
    #     logger.info(f'Удалили элемент staffrole: {staffrole}')
    #     staffrole = StaffRole.objects.all()
    #     return render(request, "project/staffrole_table.html", context={"staffrole": staffrole, "title": "Справочник"})
    if todo == 'create':
        name_staffrole = request.POST.get("name_staffrole")
        staffrole = StaffRole(name_staffrole=name_staffrole)
        staffrole.save()
        logger.info(f'Добавили элемент Own_car: {staffrole}')

        staffrole = StaffRole.objects.all()
        return render(request, "prjcalendar/staffrole_table.html", context={"staffrole": staffrole, "title": "Справочник"})
    elif todo == 'read':
        staffrole = StaffRole.objects.all()
        logger.info(f'Распечатали список Own_car: {staffrole}')
        return render(request, "prjcalendar/staffrole_table.html", context={"staffrole": staffrole, "title": "Справочник"})

# ______________заполнение служебных спрвочников_______________________





# @login_required
# def show_journal_vacations_staff_month(request, month):
    
#     now = datetime.datetime.now()
#     dt = calendar.monthrange(now.year, month)[1]
#     date_start = datetime.datetime.strptime(f"{now.year}-1-{month}", "%Y-%d-%m")
#     date_finish = datetime.datetime.strptime(f"{now.year}-{dt}-{month}", "%Y-%d-%m")
#     staff_date = show_journal_vacations_staff(request, date_start, date_finish)
#     return render(request, 'project/staff_vacations.html', staff_date)


# @login_required
# def show_journal_vacations_staff(request, date_start, date_finish):

#     staff_date = show_table_staff_vac(date_start = date_start, date_finish = date_finish)
#     staff_date["date_start"] = date_start
#     staff_date["date_finish"] = date_finish
#     staff_date["form"] = ProjectForm()
#     staff_date["title"] = "Сотрудники - отпуск"
    
#     return staff_date


# @login_required
# def show_vacations_staff(request):
    
#     staff = Staff.objects.all().order_by("name_family")
#     staff_vac = []
#     staff_line = []
#     today = datetime.datetime.now()
#     for i in staff:
#         # print(f"staff = {i.name_family} {i.name_first} {i.name_second}")     
#         staff_line.append(f"{i.name_family} {i.name_first} {i.name_second}")
#         staff_line.append(Staff_vacations.objects.filter(staffID=i.pk).filter(date_vacations__year=today.year).count())
#         for j in range(0,12):
#             # staff_vacations = Staff_vacations.objects.filter(id=i.pk).filter(created_at__date_work.month = i+1)
#             staff_vacations = Staff_vacations.objects.filter(staffID=i.pk).filter(date_vacations__year=today.year, date_vacations__month=j+1).order_by('date_vacations')  
#             if staff_vacations:
#                 # print(f"месяц = {j+1} - staff_vacations = ({staff_vacations}) {staff_vacations.count()}")     
#                 # print(f"месяц = {j+1} - staff_vacations = ({staff_vacations.first().date_vacations} - {staff_vacations.last().date_vacations}) дней {staff_vacations.count()}")
#                 staff_line.append(f"({staff_vacations.first().date_vacations.strftime("%d.%m")} - {staff_vacations.last().date_vacations.strftime("%d.%m")}) дней - {staff_vacations.count()}")
#             else:
#                 staff_line.append("-")
#         staff_vac.append(staff_line)
#         staff_line = []
        
#     return render(request, 'project/staff_vacations_shot.html', {"staff_vac": staff_vac, "title": "График отпусков"})


# @login_required
# def edit_vacations_staff(request, projects_id=13, stage_id=46):
#     '''
#     # Сюда projects_id (Сотрудники) и stage_id (отпуск) ставятся из базы
#     '''

#     # projects = Project.objects.all()
#     # staff = Staff.objects.filter(isPrj=True)
#     is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
#     if is_ajax:
#         # print(f"is_ajax = да, request = {request}")
#         if request.method == 'POST':
#             staff = Staff.objects.filter()

#             if request.POST.get('fio') != "":
#                 fio = request.POST.get('fio')
#             if request.POST.get('date') != "":
#                 date_vacations = request.POST.get('date')
#             # else:
#             #     date_vacations = '2024-01-01'
#             if request.POST.get('people') != "":
#                 people = int(request.POST.get('people'))
#             # print(f'fio = {fio} , date_vacations = {date_vacations}')
#             # work = 'Отпуск'
#             for st in staff:
#                 fio_st = f'{st.name_family} {st.name_first[:1]}.{st.name_second[:1]}.'
#                 if fio == fio_st:
#                     staff = st
#             filterargs = {'staffID': staff.pk, 'date_vacations': date_vacations}
#             # print(f'filterargs = {filterargs}')
#             if not Staff_vacations.objects.filter(**filterargs):
#                 # dates = Project.objects.get(pk=projects_id).name_prj
#                 # stage = Stages.objects.get(pk=stage_id).stage_doc
#                 dates = 'Отпуск'
#                 # dates1 = Staff_prj.objects.filter(**filterargs)
#                 # print(f"dates = {dates}")
#                 # if dates != dates1:
#                 # print(f"dates = {dates}")
#                 staff_vac = Staff_vacations(staffID=staff, date_vacations=date_vacations)
#                 staff_vac.save()
#                 people += 1
#                 logger.info(
#                     'Сохранили запись отпуска сотрудника: %s', staff_vac)
#             else:
#                 dates = ""
#                 staff_vac = Staff_vacations.objects.filter(**filterargs)
#                 staff_vac.delete()
#                 people -= 1
#                 logger.info('Удалили запись отпуска сотрудника')

#             # dates = Project.objects.get(pk=projects_id).name_prj
#             date_s = {'dates': dates, 'people': people}
#             # json_data = json.dumps(dates)
#             json_data = json.dumps(date_s)
#             # json_data_people = json.dumps(people)

#             # print(json_data)
#             return JsonResponse(json_data, safe=False)
#         return JsonResponse({'status': 'Invalid request'}, status=400)
#     elif request.method == 'POST':
#         date_today = datetime.datetime.today()
#         if request.POST.get('date_start') != "":
#             # date_start = request.POST.get('date_start')
#             date_start = datetime.datetime.strptime(
#                 request.POST.get('date_start'), '%Y-%m-%d')
#         else:
#             date_start = date_start = date_today
#         if request.POST.get('date_finish') != "":
#             date_finish = datetime.datetime.strptime(
#                 request.POST.get('date_finish'), '%Y-%m-%d')
#         else:
#             date_finish = date_today + datetime.timedelta(days=14)
#         if date_finish < date_start:
#             date_finish = date_start
#     else:
#         date_today = datetime.date.today()
#         date_start = datetime.date(date_today.year, date_today.month, 1)
#         # date_start = date_today - datetime.timedelta(days=7)
#         date_finish = date_today + datetime.timedelta(days=31)

#     staff_date = show_journal_vacations_staff(request, date_start, date_finish)

#     # staff_date = show_table_staff_vac(date_start = date_start, date_finish = date_finish)
#     # staff_date["date_start"] = date_start
#     # staff_date["date_finish"] = date_finish
#     # staff_date["form"] = ProjectForm()
#     # staff_date["title"] = "Сотрудники - отпуск"

#     return render(request, 'project/staff_vacations.html', staff_date)


# def show_table_staff_vac(date_start = datetime.date.today(), date_finish = datetime.date.today()):
#         '''
#             Отображает таблицу с отпусками сотрудников
#         '''
#         date = date_start
#         staff = Staff.objects.order_by('name_family')
#         staff_list = []
#         staff_list.append("Дата/Сотрудники")
#         # staff_list_
#         for st in staff:
#             fio = f'{st.name_family} {st.name_first[:1]}.{st.name_second[:1]}.'
#             staff_list.append(fio)
#         dates = []
#         delta = date_finish - date
#         days = delta.days
#         people = 0
#         # print(f"date_start = {date}, date_finish = {date_finish}, staff_list = {staff_list}")

#         for i in range(days+1):
#             date_l = []
#             date_l.append(date)
#             for st in staff:
#                 # date_x =[]
#                 filterargs = {'staffID': st.pk, 'date_vacations': date}
#                 st_v = Staff_vacations.objects.filter(**filterargs).first()
#                 # print(f"st = {st}, st_v = {st_v}, date_x = {date_x}")
#                 if st_v:
#                     date_l.append("Отпуск")
#                     people += 1
#                 else:
#                     date_l.append("")
#                 # print(f"st = {st}, st_v = {st_v}, date_x = {date_x}")
#                 # date_l.append(date_x)
#                 # print(f"date_l = {date_l}")
            
#             dates.append(date_l)
#             # print(f"date = {date}, dates = {dates}")

#             date += datetime.timedelta(days=1)


        
#         return {'dates': dates, 'people': people, 'staff': staff_list}
