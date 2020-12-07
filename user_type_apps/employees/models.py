from accounts.models import Profile
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    code = models.CharField(max_length=10, null=True)
    report_to = models.ForeignKey(User, related_name='assigned_employees', on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.user)
    