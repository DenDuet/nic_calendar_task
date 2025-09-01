from django.db import models

# Create your models here.

class StaffRole(models.Model):
    '''роль - генеральный директор, менеджер по развитию бизнеса, водитель, водитель-упаковщик и пр.
    ID
    Наименование - name_staffrole'''

    name_staffrole = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return f'{self.name_staffrole}'



class Progress(models.Model):
    '''Прогресс - В процессе, Завершен
    ID
    Наименование - name_progress'''

    name_progress = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return f'{self.name_progress}'


class Customer(models.Model):
    '''
    Заказчик и его данные 
    '''
    name_firm = models.CharField(max_length=100, unique=True, blank=False)
    name_contact = models.CharField(max_length=100, unique=False, blank=True)
    phone = models.CharField(max_length=30, unique=False, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    comments = models.CharField(max_length=200, unique=False, blank=True)
    isDeleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name_firm}'


class Staff(models.Model):
    '''
    ID
    ФИО - name_family + name_first + name_second
    должность - ссылка на справочник должностей - roleID
    телефон - phone
    email - email
    День рождения - birthday
    Роль в компании - roleID
    isPrj - участвует в проектах
    isDeleted - маркет удаления объекта'''

    name_family = models.CharField(max_length=30, unique=False, blank=True)
    name_first = models.CharField(max_length=30, unique=False)
    name_second = models.CharField(max_length=30, unique=False, blank=True)
    birthday = models.DateField(auto_now_add=False, blank=True, null=True)
    roleID = models.ForeignKey(
        StaffRole, on_delete=models.PROTECT, blank=True, null=True)
    phone = models.CharField(max_length=30, unique=False, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    isPrj = models.BooleanField(default=False)
    isDeleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name_first} {self.name_second} {self.name_family}'


class Project(models.Model):
    '''
    ID
    Название проекта - текст - name_prj
    Номер договора - текст - number_prj
    Дата начала - дата без автозаполнения - date_start
    Дата окончания - дата без автозаполнения - date_finish

    Описание работ по этапам - комментарии
    Сумма по этапам - число - пока пропускаем!!!
    Сумма итого – число - sum_prj
    Документы расходные (cust_docs_ID) и услуги собственные (our_docs_ID) списком из списка закрывающих документов - делаем по-другому!!!
    Список человеко/смен или сотрудников по датам работ (на будущее) - пока пропустим
    Список машин и расходов на машины - пока пропустим'''

    name_prj = models.CharField(max_length=200, unique=False)
    # number_prj = models.CharField(max_length=20, unique=False)
    date_start = models.DateField(auto_now_add=False)
    date_finish = models.DateField(auto_now_add=False)
    contact_customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, blank=True, null=True)
    # contact_self = models.ForeignKey(
        # Staff, on_delete=models.PROTECT, blank=True, null=True)

    comments = models.TextField(blank=True)
    sum_prj = models.DecimalField(  
        default=99999999.99, max_digits=12, decimal_places=2)
    progress = models.ForeignKey(
        Progress, on_delete=models.PROTECT, blank=True, null=True)
    isDeleted = models.BooleanField(default=False)

    def __str__(self):
        return f'Проект: {self.name_prj}, даты работы ({self.date_start} -  {self.date_finish})'


class Staff_prj(models.Model):
    '''
    ID
    staffID - ID сотрудника
    prjID - ID проекта
    date_work - дата, когда проводилась работа
    work - что делали, комментарий'''

    staffID = models.ForeignKey(
        Staff, on_delete=models.PROTECT, blank=True, null=True)
    prjID = models.ForeignKey(
        Project, on_delete=models.PROTECT, blank=True,  null=True)
    work = models.TextField(unique=False)
    date_work = models.DateField(auto_now_add=False)

    def __str__(self):
        return f'{self.work}'    