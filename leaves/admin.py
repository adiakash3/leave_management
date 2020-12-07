from django.contrib import admin
from .models import *

admin.site.register(LeaveType)
admin.site.register(Leave)
admin.site.register(LeaveStatus)
admin.site.register(FinancialYear)
admin.site.register(FinancialYearLeaveConfig)
admin.site.register(EmployeeFYL)
