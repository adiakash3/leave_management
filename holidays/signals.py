from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


# @receiver(post_save, sender=HolidayCalendar)
# def add_which_day_only_after_holday_created(sender, instance, created, **kwargs):
#     """add_which_day_only_after_holday_date_created"""
#     instance.day = instance.holiday_on.strftime("%A")
#     instance.save()