from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Customer

import logging

logger = logging.getLogger(__name__)

# __________________Контантные лица_____________________________


@login_required
def read_customer(request):
    customer = Customer.objects.all()
    # print(staff)
    logger.info(f'Распечатали список контактных лиц: {customer}')
    return render(request, "prjcalendar/customer_table.html", context={"customer": customer, "title": "Заказчик"})


@login_required
def create_customer(request):

    if request.method == 'POST':
        # form = StaffForm(request.POST)    
        name_firm = " ".join(request.POST.get("name_firm").split())
        name_contact = " ".join(request.POST.get("name_contact").split())
        phone = " ".join(request.POST.get("phone").split())
        email = request.POST.get("email")
        comments = " ".join(request.POST.get("comments").split())
       
        customer = Customer(name_firm=name_firm, name_contact=name_contact, phone=phone, email=email, comments=comments)
        customer.save()
        customer = Customer.objects.all()
        return render(request, 'prjcalendar/customer_table.html', {"request": request, "customer": customer, "title": "Заказчик"})

    else:
        customer = Customer.objects.all()

    return render(request, 'prjcalendar/customer_new.html', {'customer': customer, "title": "Заказчик"})


@login_required
def edit_customer(request, customer_id: int):
    # staff = Staff.objects.get(pk=staff_id)
    if request.method == 'POST':
        customer = Customer.objects.get(pk=customer_id)
        if request.POST.get('name_firm') != "":
            customer.name_firm = " ".join(request.POST.get("name_firm").split())
        if request.POST.get('name_contact') != "":
            customer.name_contact = " ".join(request.POST.get("name_contact").split())
        if request.POST.get('phone') != "":
            customer.phone = " ".join(request.POST.get("phone").split())
        if request.POST.get("email")!="":            
            customer.email = request.POST.get("email")
        if request.POST.get('comments') != "":
            customer.comments = " ".join(request.POST.get("comments").split())


        customer.save()
        logger.info(f'Успешно обновили данные сотрудников: {customer_id}.')
        customer = Customer.objects.all()

        return render(request, "prjcalendar/customer_table.html", context={"customer": customer, "title": "Заказчик"})

    else:
        customer = Customer.objects.get(pk=customer_id)


    return render(request, 'prjcalendar/customer_edit.html', {'customer': customer, "title": "Заказчик"})
