# login_activity/urls.py
from django.urls import path
from .views import list_activity

urlpatterns = [
    path('', list_activity, name='list_activity'),
]
