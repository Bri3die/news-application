from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from news.models import Article, Newsletter


class Command(BaseCommand):
    """Command to create user groups with their permissions."""
    
    help = 'Creates Reader, Editor, and Journalist groups with permissions'

    def handle(self, *args, **options):
        self.stdout.write('Creating groups and permissions...')

        # Get content types
        article_ct = ContentType.objects.get_for_model(Article)
        newsletter_ct = ContentType.objects.get_for_model(Newsletter)

        # Create Reader group (view only)
        reader_group, created = Group.objects.get_or_create(name='Reader')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Reader group'))
        else:
            self.stdout.write('Reader group already exists')

        reader_permissions = Permission.objects.filter(
            content_type__in=[article_ct, newsletter_ct],
            codename__startswith='view'
        )
        reader_group.permissions.set(reader_permissions)
        self.stdout.write(f'  Added {reader_permissions.count()} permissions to Reader')

        # Create Editor group (view, change, delete)
        editor_group, created = Group.objects.get_or_create(name='Editor')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Editor group'))
        else:
            self.stdout.write('Editor group already exists')

        editor_permissions = Permission.objects.filter(
            content_type__in=[article_ct, newsletter_ct],
            codename__in=[
                'view_article', 'change_article', 'delete_article',
                'view_newsletter', 'change_newsletter', 'delete_newsletter'
            ]
        )
        editor_group.permissions.set(editor_permissions)
        self.stdout.write(f'  Added {editor_permissions.count()} permissions to Editor')

        # Create Journalist group (full CRUD)
        journalist_group, created = Group.objects.get_or_create(name='Journalist')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Journalist group'))
        else:
            self.stdout.write('Journalist group already exists')

        journalist_permissions = Permission.objects.filter(
            content_type__in=[article_ct, newsletter_ct]
        )
        journalist_group.permissions.set(journalist_permissions)
        self.stdout.write(f'  Added {journalist_permissions.count()} permissions to Journalist')

        self.stdout.write(self.style.SUCCESS('Done!'))
