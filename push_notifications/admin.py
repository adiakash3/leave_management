from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(FcmSetting)
admin.site.register(MobileDevice)
admin.site.register(MobileNotification)