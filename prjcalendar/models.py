from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

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
    color = models.CharField(
        max_length=7, default="#007bff", verbose_name="Цвет проекта")
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


class UserGroup(models.Model):
    '''Группа пользователей с определенными правами доступа'''
    name = models.CharField(max_length=100, unique=True,
                            verbose_name="Название группы")
    description = models.TextField(blank=True, verbose_name="Описание группы")
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        verbose_name="Права доступа"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Группа пользователей"
        verbose_name_plural = "Группы пользователей"
        ordering = ['name']

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    '''Расширенный профиль пользователя с правами доступа'''
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name="Пользователь")
    user_group = models.ForeignKey(
        UserGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Группа пользователя"
    )
    staff_member = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Сотрудник"
    )
    can_view_projects = models.BooleanField(
        default=False, verbose_name="Просмотр проектов")
    can_edit_projects = models.BooleanField(
        default=False, verbose_name="Редактирование проектов")
    can_delete_projects = models.BooleanField(
        default=False, verbose_name="Удаление проектов")
    can_view_staff = models.BooleanField(
        default=False, verbose_name="Просмотр сотрудников")
    can_edit_staff = models.BooleanField(
        default=False, verbose_name="Редактирование сотрудников")
    can_view_customers = models.BooleanField(
        default=False, verbose_name="Просмотр заказчиков")
    can_edit_customers = models.BooleanField(
        default=False, verbose_name="Редактирование заказчиков")
    can_manage_users = models.BooleanField(
        default=False, verbose_name="Управление пользователями")
    can_view_reports = models.BooleanField(
        default=False, verbose_name="Просмотр отчетов")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"Профиль {self.user.username}"

    def has_permission(self, permission_name):
        """Проверяет наличие конкретного права у пользователя"""
        if hasattr(self, permission_name):
            return getattr(self, permission_name)
        return False

    def get_all_permissions(self):
        """Возвращает список всех прав пользователя"""
        permissions = []
        for field in self._meta.fields:
            if field.name.startswith('can_') and isinstance(field, models.BooleanField):
                if getattr(self, field.name):
                    permissions.append(field.name)
        return permissions


class ProjectAccess(models.Model):
    '''Доступ к конкретным проектам для пользователей'''
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь")
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, verbose_name="Проект")
    can_view = models.BooleanField(default=True, verbose_name="Просмотр")
    can_edit = models.BooleanField(
        default=False, verbose_name="Редактирование")
    can_delete = models.BooleanField(default=False, verbose_name="Удаление")
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_project_access',
        verbose_name="Предоставлено пользователем"
    )
    granted_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата предоставления")

    class Meta:
        verbose_name = "Доступ к проекту"
        verbose_name_plural = "Доступы к проектам"
        unique_together = ['user', 'project']

    def __str__(self):
        return f"{self.user.username} - {self.project.name_prj}"


class Task(models.Model):
    """Модель для задач в календаре"""
    name = models.CharField(max_length=200, verbose_name="Название задачи")
    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, verbose_name="Сотрудник")
    day = models.IntegerField(verbose_name="День месяца")
    duration = models.IntegerField(
        default=1, verbose_name="Длительность (дни)")
    color = models.CharField(
        max_length=7, default="#007bff", verbose_name="Цвет")
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Проект")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Создал")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата обновления")
    is_deleted = models.BooleanField(default=False, verbose_name="Удалено")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['staff', 'day', 'created_at']
        # Одна задача на проект в день у сотрудника
        unique_together = ['staff', 'day', 'project']

    def __str__(self):
        return f"{self.name} - {self.staff.name_family} ({self.day} день)"

    def save(self, *args, **kwargs):
        # Автоматически устанавливаем создателя если не указан
        if not self.pk and not self.created_by_id:
            from django.contrib.auth.models import AnonymousUser
            if hasattr(self, '_current_user') and self._current_user and not isinstance(self._current_user, AnonymousUser):
                self.created_by = self._current_user
        super().save(*args, **kwargs)
