from django import forms
# from django.conf import settings


class ImageForm(forms.Form):
    image = forms.ImageField()
    
    
class RecipeForm(forms.Form):
    name = forms.CharField(max_length=50)
    description = forms.CharField()
    steps = forms.CharField()
    add_date = forms.DateTimeField()  
    image = forms.ImageField()
    author = forms.CharField()
    ingredients = forms.CharField() 
    
    
class Category(forms.Form):
    category_name = forms.CharField(max_length=50)
    description = forms.CharField() 
    
class UserForm(forms.Form):
    username = forms.CharField(max_length=50)
    email = forms.EmailField()
    phone = forms.CharField(max_length=50)
    address = forms.CharField(max_length=50)    
    reg_date = forms.DateTimeField()    
