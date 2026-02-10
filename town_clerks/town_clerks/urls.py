from django.contrib import admin
from django.urls import path, include
from clerks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.hub, name='hub'),
    path('clerks/', include('clerks.urls')),
]
