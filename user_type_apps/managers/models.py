from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Profile
from user_type_apps.employees.models import *
User = get_user_model()


class Manager(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='manager', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.employee)
    