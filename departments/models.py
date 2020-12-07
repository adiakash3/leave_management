from accounts.models import Profile
from django.contrib.auth import get_user_model
from django.db import models
from user_type_apps.employees.models import Employee

User = get_user_model()


class Organisation(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class Department(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='organisation')
    name = models.CharField(max_length=100)
    no_leaves = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class EmployeeDepartment(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='emp_department',blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE,blank=True, null=True)
    joined_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.employee)
