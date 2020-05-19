"""linx URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from . import views

urlpatterns = [
    path(r'^admin/', admin.site.urls),
    path(r'^messages/', views.get_messages, name='messages'),
    path(r'^get_convo/', views.get_convo, name='convo'),
    path(r'^add_message/', views.add_message, name='addMessage'),
    path(r'^sign_in/', views.sign_in, name='signin'),
    path(r'^sign_up/', views.sign_up, name='signup'),
    path(r'^get_profile/', views.get_profile, name='getprofile'),
    path(r'^update_profile/', views.update_profile, name='updateprofile'),
]
