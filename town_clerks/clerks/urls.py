from django.urls import path
from . import views

app_name = 'clerks'

urlpatterns = [
    path('', views.hub, name='home'),
    path('hub/', views.hub, name='hub'),
    path('ingest/', views.ingest, name='ingest'),

    path('activity/', views.activity_list, name='activity_list'),

    # Section URLs
    path('vets/', views.vet_list, name='vet_list'),
    path('vets/raw/', views.vets_raw, name='vets_raw'),
    path('vets/<str:pk>/', views.vet_detail, name='vet_detail'),
    path('marriages/', views.marriage_list, name='marriage_list'),
    path('marriages/raw/', views.marriages_raw, name='marriages_raw'),
    path('marriages/<str:pk>/', views.marriage_detail, name='marriage_detail'),
    path('vitals/', views.vitals_list, name='vitals_list'),
    path('vitals/raw/', views.vitals_raw, name='vitals_raw'),
    path('vitals/<str:pk>/', views.vitals_detail, name='vitals_detail'),
    path('transmitel/', views.transmitel_list, name='transmitel_list'),
    path('transmitel/raw/', views.transmitel_raw, name='transmitel_raw'),
    path('transmitel/<str:pk>/', views.transmitel_tx_detail, name='transmitel_tx_detail'),

    path('transmitel_report/<int:pk>/', views.transmitel_detail, name='transmitel_detail'),

    # Clerk keyed transmittal report (app-managed)
    path('transmittal/new/', views.transmittal_entry, name='transmittal_entry'),
    path('transmittal/print/<int:pk>/', views.transmittal_print, name='transmittal_print'),
]
