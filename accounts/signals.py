from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def assign_role_permissions(sender, instance, created, **kwargs):
    if created:  # Only assign permissions when a new user is created
        if instance.role == 'admin':
            group, _ = Group.objects.get_or_create(name='Admin')
            permissions = Permission.objects.filter(codename__in=['can_manage_users'])
        elif instance.role == 'teacher':
            group, _ = Group.objects.get_or_create(name='Teacher')
            permissions = Permission.objects.filter(codename__in=['can_grade_students'])
        else:  # student
            group, _ = Group.objects.get_or_create(name='Student')
            permissions = Permission.objects.filter(codename__in=['can_view_courses'])
        
        group.permissions.set(permissions)
        instance.groups.add(group)