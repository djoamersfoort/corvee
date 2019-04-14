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
from .src import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('main/', views.Main.as_view(), name='main'),
    path('main/<str:day>/', views.Main.as_view(), name='main'),
    path('ack/<int:pk>', views.Acknowledge.as_view(), name='acknowledge'),
    path('insuff/<int:pk>', views.Insufficient.as_view(), name='insufficient'),
    path('absent/<str:day>/<int:pk>/', views.Absent.as_view(), name='absent'),
    path('renew/<str:day>/', views.Renew.as_view(), name='renew'),
    path('logoff/', views.LogoffView.as_view(), name='logoff'),
    re_path(r'oauth/.*', views.LoginResponseView.as_view()),
    path('', views.LoginView.as_view(), name='login')
]
