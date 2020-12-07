from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
import logging

logger = logging.getLogger(__name__)


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class Role(models.Model):
    ADMIN = 1
    MANAGER = 2
    TEAM_LEADER = 3
    EMPLOYEE = 4

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (TEAM_LEADER, 'Team Leader'),
        (EMPLOYEE, 'Employee'),
    )
    id = models.PositiveSmallIntegerField(('select role'), choices=ROLE_CHOICES, primary_key=True)

    def __str__(self):
        return self.get_id_display()


class User(AbstractUser):
    ''' Main User '''
    username = None
    email = models.EmailField(_('email address'), unique=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    roles = models.ManyToManyField(Role)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        if self.email:
            return str(self.email)
        if self.mobile_number:
            return str(self.mobile_number)
        if self.first_name:
            return self.first_name
        if self.last_name:
            return self.last_name


def image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/job_image/user_<id>/<filename>
    return 'profile/user_{0}/{1}'.format(instance.user.id, filename)


class Profile(models.Model):
    MALE = 'male'
    FEMALE = 'female'
    PREFER_NOT_TO_SAY = 'prefer_not_to_say'

    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (PREFER_NOT_TO_SAY, 'Prefer not to say'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', blank=True, null=True)
    image = models.ImageField(upload_to=image_path, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    pincode = models.CharField(max_length=10,blank=True, null=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    age = models.PositiveSmallIntegerField(blank=True, null=True)
    gender = models.CharField(choices=GENDER_CHOICES,max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return str(self.user)


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         logger.info('user and profile created')
#         profile, is_created = Profile.objects.get_or_create(user=instance)


class EmailOtp(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    otp = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.otp) + str(self.email)

