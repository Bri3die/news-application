from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def assign_user_to_group(sender, instance, created, **kwargs):
    """Assign new users to the correct group based on their role."""
    
    # Only run for new users
    if not created:
        return

    role_to_group = {
        'reader': 'Reader',
        'editor': 'Editor',
        'journalist': 'Journalist',
    }

    group_name = role_to_group.get(instance.role)

    if group_name:
        group = Group.objects.filter(name=group_name).first()
        if group:
            instance.groups.add(group)
