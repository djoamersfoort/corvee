"""corvee URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from corvee.src import views
from corvee.src import api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('leden/', views.Leden.as_view(), name='leden'),
    path('leden/<str:day>/', views.Leden.as_view(), name='leden'),
    path('main/', views.Main.as_view(), name='main'),
    path('ack/<int:pk>', views.Acknowledge.as_view(), name='acknowledge'),
    path('insuff/<int:pk>', views.Insufficient.as_view(), name='insufficient'),
    path('punish/<int:pk>', views.Punishment.as_view(), name='punishment'),
    path('absent/<int:pk>/', views.Absent.as_view(), name='absent'),
    path('renew/', views.Renew.as_view(), name='renew'),
    path('logoff/', views.LogoffView.as_view(), name='logoff'),
    path('api/v1/selected', api.SelectedV1.as_view(), name='selected_api'),
    path('api/v1/status', api.StatusV1.as_view(), name='status_api'),
    path('api/v1/renew', api.RenewV1.as_view(), name='renew_api'),
    path('api/v1/ack/<int:pk>', api.AcknowledgeV1.as_view(), name='acknowledge_api'),
    path('api/v1/insuff/<int:pk>', api.InsufficientV1.as_view(), name='insufficient_api'),
    path('api/v1/punish/<int:pk>', api.PunishmentV1.as_view(), name='punishment_api'),
    path('api/v1/absent/<int:pk>', api.AbsentV1.as_view(), name='absent_api'),
    re_path(r'oauth/.*', views.LoginResponseView.as_view()),
    path('', views.LoginView.as_view(), name='login')
]
