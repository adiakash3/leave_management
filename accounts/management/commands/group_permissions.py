from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

# Codename, model

ADMIN_PERMISSIONS = (

    ('edit_agent', 'user'),
    ('add_agent', 'user'),
    ('view_agent', 'user'),
    ('add_job', 'user'),
    ('edit_job', 'user'),
    ('unassign_job', 'user'),
)

AGENT_PERMISSIONS = (

)

MANAGER_PERMISSIONS = (
    ('view_agent', 'user'),
    ('add_job', 'user'),
    ('edit_job', 'user'),
    ('unassign_job', 'user'),
)


class Command(BaseCommand):
    help = 'create groups with permissions for different roles'

    def handle(self, *args, **kwargs):
        Permission.objects.all().delete()
        self.add_permissions('Admin', ADMIN_PERMISSIONS, 'success - admin group created.')
        self.add_permissions('Agent', AGENT_PERMISSIONS, 'success - agent group created.')
        self.add_permissions('Manager', MANAGER_PERMISSIONS, 'success - manager group created.')
        
    def add_permissions(self, group_name, permissions_tuple, message):
        group, created = Group.objects.get_or_create(name=group_name)

        for codename, model in permissions_tuple:
            content_type = ContentType.objects.get(model=model)
            name = 'Can {}'.format(codename.replace('_', ' '))
            permission, created = Permission.objects.get_or_create(
                codename=codename, name=name, content_type=content_type)
            group.permissions.add(permission)
        self.stdout.write(self.style.SUCCESS(message))
