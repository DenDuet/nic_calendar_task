from django.conf import settings
from django.conf.urls.static import static
from django.urls import path


from . import views

urlpatterns = [

    path("", views.index, name='index'),
    #     path('init_bases/', views.init_bases, name='initialize bases'),
    path('read_users/', views.read_users, name='read users base'),
#     path('read_caregory/', views.read_caregory, name='read goods base'),
#     path('category/create/', views.create_category,
#          name='create category to base'),
#     path('category/edit/<int:cat_id>/',
#          views.edit_category, name='edit category base'),
#     path('category/delete/<int:cat_id>/',
#          views.delete_category, name='delete category base'),
#     path('main_recipe/<int:cat_id>/', views.main_recipe,
#          name='show recipes and categories base'),
#     path('recipe/create/', views.create_recipe, name='create recipe to base'),
#     path('recipe/edit/<int:rcp_id>/', views.edit_recipe, name='edit recipe base'),
#     path('recipe/delete/<int:rcp_id>/',
#          views.delete_recipe, name='delete recipe base'),
#     path('upload/<int:recipe_id>/', views.upload_image, name='upload_image'),
#     path('journal/create/<int:rcp_id>/', views.create_jrn,
#          name='create journal to base'),
#     path('journal/edit/<int:rcp_id>/<int:cat_id>/', views.edit_jrn,
#          name='edit journal to base'),
#     path('journal/delete/<int:jrn_id>/', views.delete_jrn,
#          name='delete journal to base'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
