# login_activity/urls.py
from django.urls import path
from .views import list_activity

urlpatterns = [
    path('activity/', list_activity, name='login_activity_list'),
]
