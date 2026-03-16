from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import CustomUser, Publisher, Article, Newsletter


class CustomUserAdmin(UserAdmin):
    """Admin config for CustomUser with role and subscription fields."""
    
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
        ('Subscriptions', {'fields': ('subscribed_publishers', 'subscribed_journalists')}),
    )

    def save_related(self, request, form, formsets, change):
        """Auto-assign user to the correct group based on their role."""
        super().save_related(request, form, formsets, change)

        user = form.instance

        role_to_group = {
            'reader': 'Reader',
            'editor': 'Editor',
            'journalist': 'Journalist',
        }

        group_name = role_to_group.get(user.role)

        if group_name:
            group = Group.objects.filter(name=group_name).first()
            if group:
                # Remove from all role groups first
                user.groups.remove(
                    *Group.objects.filter(name__in=['Reader', 'Editor', 'Journalist'])
                )
                # Add to correct group
                user.groups.add(group)


class ArticleAdmin(admin.ModelAdmin):
    """Admin config for Article model."""
    
    list_display = ('title', 'author', 'publisher', 'approved', 'created_at')
    list_filter = ('approved', 'publisher', 'created_at')
    search_fields = ('title', 'content')


class NewsletterAdmin(admin.ModelAdmin):
    """Admin config for Newsletter model."""
    
    list_display = ('title', 'author', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('title', 'description')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Publisher)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Newsletter, NewsletterAdmin)
