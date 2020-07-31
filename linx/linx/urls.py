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
    path('get_conversation_list/', views.get_conversation_list, name='get_conversation_list'),
    path('get_conversation/', views.get_conversation, name='get_conversation'),
    path('add_message/', views.add_message, name='addMessage'),
    path('sign_in/', views.sign_in, name='signin'),
    path('sign_up/', views.sign_up, name='signup'),
    path('get_profile/', views.get_profile, name='getprofile'),
    path('update_profile/', views.update_profile, name='updateprofile'),
    path('get_image/', views.get_image, name='getImage'),
    path('save_image/', views.save_image, name='saveImage'),
    path('react_to_image/', views.react_to_image, name='reactToImage'),
    path('is_valid_linx_zip/', views.is_valid_lix_zip, name='isValidLinxZip')
]
