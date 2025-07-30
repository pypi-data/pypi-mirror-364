# login_activity/models.py
from django.db import models
from django.contrib.auth import get_user_model

class LoginActivity(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} connecté depuis {self.ip_address} à {self.timestamp}"
