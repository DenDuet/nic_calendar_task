import json
import datetime
from django.http import JsonResponse
from django.shortcuts import redirect, render

from django.contrib.auth.decorators import login_required

from .models import Customer, Progress, Project, Staff, Staff_prj
from .forms import ProjectForm
import logging
# from django.db.models import Q

logger = logging.getLogger(__name__)


# __________________Проекты_____________________________________


@login_required
def read_projects(request):
    if request.method == 'POST':
        date_today = datetime.datetime.now()
        if request.POST.get('date_start') != "":
            # date_start = request.POST.get('date_start')
            date_st = datetime.datetime.strptime(
                request.POST.get('date_start'), '%Y-%m-%d')
        else:
            date_st = date_st = date_today
        if request.POST.get('date_finish') != "":
            date_fin = datetime.datetime.strptime(
                request.POST.get('date_finish'), '%Y-%m-%d')
        else:
            date_fin = date_today + datetime.timedelta(days=14)
        if date_fin < date_st:
            date_fin = date_st
    else:
        date_today = datetime.datetime.now()
        date_st = date_today - datetime.timedelta(days=180)
        date_fin = date_today + datetime.timedelta(days=14)

    projects = Project.objects.filter(
        date_start__range=[date_st, date_fin]).filter(
        date_finish__range=[date_st, date_fin])
    logger.info(f'Распечатали список проектов: {projects}')
    return render(request, "prjcalendar/projects_table.html", context={"date_start": date_st, "date_finish": date_fin, "projects": projects, "title": "Проекты"})


@login_required
def create_projects(request):
    if request.method == 'POST':
        # print(f"roles = {roles}")

        if request.POST.get('customerID') != "":
            contact_customer = Customer.objects.get(
                name_firm=request.POST.get('customerID'))
        # if request.POST.get('contact_self') != "":
        #     contact_self = Staff.objects.get(
        #         contact_self=request.POST.get('contact_self'))
        if request.POST.get('name_prj') != "":
            name_prj = " ".join(request.POST.get("name_prj").split())
        if request.POST.get('sum_prj') != "":
            sum_prj = request.POST.get("sum_prj")

        if request.POST.get('date_start') != "":
            date_start = datetime.datetime.strptime(
                request.POST.get('date_start'), '%Y-%m-%d')
        if request.POST.get('date_finish') != "":
            date_finish = datetime.datetime.strptime(
                request.POST.get('date_finish'), '%Y-%m-%d')
        if request.POST.get('progress') != "":
            progress = Progress.objects.get(
                name_progress=request.POST.get('progress'))            

        comments = " ".join(request.POST.get("comments").split())

        project = Project(contact_customer=contact_customer, name_prj=name_prj, progress=progress, date_start=date_start, date_finish=date_finish, sum_prj=sum_prj, comments=comments)

        project.save()
        logger.info(f'Успешно создали проект: {project}.')
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
        # return redirect(f'/read_projects/')

    else:
        form = ProjectForm()
        progress = Progress.objects.all()
        if len(progress)==0:
            progress = Progress(name_progress="Завершен")
            # print(f"progress = {progress}")
            progress.save()
            progress = Progress(name_progress="В работе")
            # print(f"progress = {progress}")
            progress.save()        
        # project = Project.objects.all()
        # staff = Staff.objects.all()
        progress = Progress.objects.all()
        customer = Customer.objects.all()

    return render(request, 'prjcalendar/projects_new.html', {'progresses':progress, 'customer': customer, 'form': form, "title": "Проекты"})


@login_required
def edit_projects(request, projects_id: int):

    if request.method == 'POST':
        project = Project.objects.get(pk=projects_id)
        if request.POST.get('customerID') != "":
            project.contact_customer = Customer.objects.get(
                name_firm=request.POST.get('customerID'))
        # if request.POST.get('contact_self') != "":
        #     project.contact_self = Customer.objects.get(
        #         contact_self=request.POST.get('contact_self'))
        if request.POST.get('name_prj') != "":
            project.name_prj = " ".join(request.POST.get("name_prj").split())
        if request.POST.get('sum_prj') != "":
            project.sum_prj = request.POST.get("sum_prj")

        if request.POST.get('date_start') != "":
            project.date_start = datetime.datetime.strptime(request.POST.get('date_start'), '%Y-%m-%d')
        if request.POST.get('date_finish') != "":
            project.date_finish = datetime.datetime.strptime(request.POST.get('date_finish'), '%Y-%m-%d')
        if request.POST.get('progress') != "":
            project.progress = Progress.objects.get(
                name_progress=request.POST.get('progress'))

        project.comments = " ".join(request.POST.get("comments").split())
        project.save()
        logger.info(f'Успешно обновили проект: {projects_id}.')
        date_today = datetime.datetime.now()
        date_st = date_today - datetime.timedelta(days=180)
        date_fin = date_today + datetime.timedelta(days=14)

        projects = Project.objects.filter(
            date_start__range=[date_st, date_fin]).filter(
            date_finish__range=[date_st, date_fin])
        logger.info(f'Распечатали список проектов: {projects}')
        return render(request, "prjcalendar/projects_table.html", context={"date_start": date_st, "date_finish": date_fin, "projects": projects, "title": "Проекты"})
        # return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

    else:
        # form = ProjectForm()
        # staff = Staff.objects.all()
        progress = Progress.objects.all()
        project = Project.objects.get(pk=projects_id)
        customer = Customer.objects.all()

    return render(request, 'prjcalendar/projects_edit.html', {'progresses': progress, 'project': project, 'customer': customer, "title": "Проекты"})



# @login_required
# def edit_projects_staff(request, projects_id: int, stage_id: int):

#     projects = Project.objects.all()
#     staff = Staff.objects.filter(isPrj=True)
#     is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
#     if is_ajax:
#         # print(f"is_ajax = да, request = {request}")
#         if request.method == 'POST':

#             if request.POST.get('fio') != "":
#                 fio = request.POST.get('fio')
#             if request.POST.get('date') != "":
#                 date_work = request.POST.get('date')
#             if request.POST.get('people') != "":
#                 people = int(request.POST.get('people'))
#             # print(f'{request.POST}')
#             work = f'Необходимые работы по проекту {Project.objects.get(pk=projects_id).name_prj} этап {Stages.objects.get(pk=stage_id)}'
#             for st in staff:
#                 fio_st = f'{st.name_family} {st.name_first[:1]}.{st.name_second[:1]}.'
#                 if fio == fio_st:
#                     staff = st
#                     # print(f'staffID = {staff.pk}')
#             filterargs = {'staffID': staff.pk, 'stageID': Stages.objects.get(pk=stage_id),
#                           'prjID': Project.objects.get(pk=projects_id), 'date_work': date_work}
#             if not Staff_prj.objects.filter(**filterargs):
#                 dates = Project.objects.get(pk=projects_id).name_prj
#                 stage = Stages.objects.get(pk=stage_id).stage_doc
#                 dates = f'{dates} {stage}'
#                 # dates1 = Staff_prj.objects.filter(**filterargs)
#                 # print(f"dates = {dates}")
#                 # if dates != dates1:
#                 # print(f"dates1 = {dates1}")
#                 staff_prj = Staff_prj(staffID=staff, stageID=Stages.objects.get(pk=stage_id), prjID=Project.objects.get(pk=projects_id),
#                                       work=work, date_work=date_work)
#                 staff_prj.save()
#                 people += 1
#                 logger.info(
#                     'Сохранили запись проекта сотрудника: %s', staff_prj)
#             else:
#                 dates = ""
#                 staff_prj = Staff_prj.objects.filter(**filterargs)
#                 staff_prj.delete()
#                 people -= 1
#                 logger.info('Удалили запись проекта сотрудника')

#             # dates = Project.objects.get(pk=projects_id).name_prj
#             date_s = {'dates': dates, 'people': people}
#             # json_data = json.dumps(dates)
#             json_data = json.dumps(date_s)
#             # json_data_people = json.dumps(people)

#             # print(json_data)
#             return JsonResponse(json_data, safe=False)
#         return JsonResponse({'status': 'Invalid request'}, status=400)

#     else:

#         staff_date = show_table_staff(stage_id, projects_id, "часть")
#         staff_date["form"] = ProjectForm()
#         staff_date["title"] = "Сотрудники в проекте"

#     return render(request, 'project/projects_work_staff.html', staff_date)



# def show_table_staff(stage_id: int, projects_id: int, text = "часть", date_start = datetime.datetime.today(), date_finish = datetime.datetime.today()):
#         if text == "часть":
#             project = Project.objects.get(pk=projects_id)
#             stage = Stages.objects.get(pk=stage_id)
#         else:
#             project = Project.objects.get(pk=10)
#             stage = Stages.objects.get(pk=8)

#         # cars = Truck.objects.all().order_by('number')
#         staff = Staff.objects.filter(isPrj=True).order_by('name_family')
#         staff_list = []
#         staff_list.append("Дата/Сотрудники")
#         # car_list = []
#         for st in staff:
#             fio = f'{st.name_family} {st.name_first[:1]}.{st.name_second[:1]}.'
#             staff_list.append(fio)      

#         if text != "все":
#             date = stage.date_start
#             date_finish = stage.date_finish                 
#         else:
#             date = date_start

#         dates = []
#         delta = date_finish - date
#         days = delta.days
#         people = 0
#         # car = 0
#         for i in range(days+1):
#             date_1 = []
#             date_2 = []
#             date_3 = []
#             date_4 = []
#             date_l = []
#             max_prj = 1
#             for st in staff:
#                 date_x =[]
                
#                 # ---------------
#                 filterargs = {'staffID': st.pk, 'date_vacations': date}
#                 st_v = Staff_vacations.objects.filter(**filterargs).first()
#                 # print(f'st_v = {st_v}')
#                 if st_v:
#                     date_x.append("Отпуск")
#                     # print(f'date_x = {date_x}')
#                 # ------------------           
                     
#                 filterargs = {'staffID': st.pk,
#                               'date_work': date}
#                 if Staff_prj.objects.filter(**filterargs):

#                     prj_id = Staff_prj.objects.filter(**filterargs)
#                     # date_x=[]
                   
#                     for i in prj_id:
#                         if text != "все":
#                             if stage.IDproject.pk == i.prjID.pk and stage.pk == i.stageID.pk:
#                                 people += 1
#                             date_x.append(Project.objects.get(pk=i.prjID.pk).name_prj + " " + Stages.objects.get(pk=i.stageID.pk).stage_doc)
#                         else:
#                             people += 1

#                         # name = Project.objects.get(
#                             # pk=i.prjID.pk).name_prj + " " + Stages.objects.get(pk=i.stageID.pk).stage_doc
#                             date_x.append(Project.objects.get(pk=i.prjID.pk).name_prj)
#                     date_l.append(date_x)
                    
#                     if len(date_x) > max_prj:
#                         max_prj = len(date_x)
                    
#                 else:
#                     if date_x:
#                         date_l.append(date_x)
#                     else:
#                         date_l.append("")
            
#             date_1.append({date: max_prj})

#             for dt_l in date_l:
#                 i = 1
#                 if len(dt_l) > 0:
#                     for dt in dt_l:
#                         if i == 1:
#                             if len(dt_l) == 1:
#                                 rowspan = max_prj
#                             else:
#                                 rowspan = 1

#                             if len(dt_l) > 0:
#                                 date_1.append({dt: rowspan})
#                             else:
#                                 date_1.append({"": rowspan})
#                         elif i == 2:
#                             # date_l.append({key: date_l_prom[key]})
#                             if len(dt_l) == 2:
#                                 rowspan = max_prj-1
#                             else:
#                                 rowspan = 1                            
#                             date_2.append({dt: rowspan})
#                         elif i == 3:
#                             if len(dt_l) == 3:
#                                 rowspan = max_prj-2
#                             else:
#                                 rowspan = 1                             
#                             date_3.append({dt: rowspan})
#                         else:                           
#                             date_4.append({dt: rowspan})
#                         i+=1
#                 else:
#                     if dt_l == "":
#                         date_1.append({"": max_prj})
#                     else:
#                         date_1.append({dt_l: max_prj})
            
#             if len(date_1) > 0:
#                 dates.append(date_1)
#                 date_1 = []            
#             if len(date_2) > 0:
#                 dates.append(date_2)
#                 date_2 = []            
#             if len(date_3) > 0:
#                 dates.append(date_3)
#                 date_3 = []            
#             if len(date_4) > 0:
#                 dates.append(date_4)
#                 date_4 = []            

#             date += datetime.timedelta(days=1)
#             # if text == "все":
#             #     project = Project.objects.get(pk=10)

        
#         return {'stage': stage, 'dates': dates, 'people': people, 'staff': staff_list, 'project': project}

# # __________________Проекты_____________________________________
