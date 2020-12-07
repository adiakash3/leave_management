from django.contrib import admin
from .models import *

admin.site.register(Shift)
admin.site.register(Break)
admin.site.register(EmployeeAttendance)
admin.site.register(EmployeeShift)
admin.site.register(LateExemptStatus)
admin.site.register(LateExempt)