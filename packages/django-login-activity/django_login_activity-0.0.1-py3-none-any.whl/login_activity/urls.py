# login_activity/urls.py
from django.urls import path
from .views import activity_list

urlpatterns = [
    path('', activity_list, name='login_activity_list'),
]
