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
    path('admin/', admin.site.urls),
    path('messages', views.get_messages, name='messages'),
    path('get_convo', views.get_convo, name='convo'),
    path('add_message', views.add_message, name='addMessage'),
    path('sign_in', views.sign_in, name='signin'),
    path('sign_up', views.sign_up, name='signup'),
    path('update_profile', views.update_profile, name='updateprofile'),
]
