# login_activity/views.py
from django.shortcuts import render
from .models import LoginActivity

def list_activity(request):
    logs = LoginActivity.objects.all().order_by('-timestamp')
    return render(request, 'login_activity/list.html', {'activities': logs})
