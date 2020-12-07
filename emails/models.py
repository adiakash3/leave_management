from django.db import models
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth import get_user_model

User = get_user_model()

class MailServerConfig(models.Model):
    """
    Mail server configurations consider only is_enabled
    """
    title = models.CharField(max_length=250)
    is_enabled = models.BooleanField(default=False)
    mail_server = models.CharField(max_length=100)
    mail_port = models.PositiveIntegerField()
    use_ssl = models.BooleanField(default=True)
    username = models.CharField(max_length=250)
    password = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title + ' is_enabled ' + str(self.is_enabled)


class Mail(models.Model):
    """ add mail content"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mails',null=True)
    to = models.CharField(max_length=250)
    status = models.CharField(max_length=250)
    subject = models.CharField(max_length=250)
    body = RichTextField(verbose_name='email body')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.subject)