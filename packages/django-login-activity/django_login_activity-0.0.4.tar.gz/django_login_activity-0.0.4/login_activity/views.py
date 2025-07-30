from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import LoginActivity

@login_required
def list_activity(request):
    logs = LoginActivity.objects.all().order_by('-timestamp')
    return render(request, 'login_activity/list.html', {'activities': logs})
