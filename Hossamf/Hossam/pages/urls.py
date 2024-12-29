from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
   path('form/', views.form, name='form'),
   path('', views.profile, name='profile'),
   path('update/', views.update_profile, name='update_profile'), 
   path('delete/<int:id>', views.delete, name='delete'), 
   path('eye/', views.eye, name='eye'),
   path('delete_profile/', views.delete_profile, name='delete_profile'),
   path('edit/<int:id>/', views.edit_patient, name='edit'),
   path('waiting_page/', views.waiting_page, name='waiting_page'),
   # path('process/', views.process_form, name='process_form'),
   path('metabolic/', views.metabolic, name='metabolic'),
   # path('check_status/', views.check_status, name='check_status'),
   path('waiting/', views.waiting, name='waiting'),

   


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


