from django.shortcuts import render
from login_activity.models import LoginActivity

def list_activity(request):
    if not request.user.is_authenticated:
        return render(request, 'login_activity/list.html', {
            'activities': [],
            'not_logged_in': True
        })

    logs = LoginActivity.objects.all().order_by('-timestamp')
    return render(request, 'login_activity/list.html', {
        'activities': logs,
        'not_logged_in': False
    })
