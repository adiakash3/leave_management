from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Profile
from user_type_apps.employees.models import Employee
User = get_user_model()


class TeamLeader(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='team_leader', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.employee)
    