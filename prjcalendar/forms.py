from django.forms import ModelForm
from prjcalendar.models import Customer, Project, Staff, StaffRole
from workcalendar.settings import DATE_INPUT_FORMATS
# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout, Submit, Field

class StaffRoleForm(ModelForm):

    class Meta:
        model = StaffRole
        fields = ['name_staffrole']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'        
        

class StaffForm(ModelForm):

    class Meta:
        model = Staff
        fields = ['birthday', 'name_first', 'name_family', 'name_second', 'roleID', 'phone', 'email', 'isPrj', 'isDeleted']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class CustomerForm(ModelForm):

    class Meta:
        model = Customer
        fields = ['name_firm', 'name_contact', 'comments', 'phone', 'email', 'isDeleted']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
                
class ProjectForm(ModelForm):

    class Meta:
        model = Project
        fields = ['name_prj', 'date_start', 'date_finish', 'sum_prj', 'isDeleted', 'comments']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            