from django.db import models

class HolidayCalendar(models.Model):
    """Holiday calender list"""
    holiday_on = models.DateField()
    name = models.CharField(max_length=250)
    day = models.CharField(max_length=15, editable=False)
    observance = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def save(self, *args, **kwargs):
        self.day = self.holiday_on.strftime("%A")
        super(HolidayCalendar, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name + ' holiday on ' +str(self.holiday_on)


