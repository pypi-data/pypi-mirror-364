from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    path = models.CharField(max_length=512)
    method = models.CharField(max_length=10)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    duration = models.FloatField(help_text="Durée de la requête en secondes")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.path} @ {self.timestamp}"
from django.db import models

# Create your models here.
