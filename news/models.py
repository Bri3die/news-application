from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Custom user model with roles for the news app."""
    
    ROLE_CHOICES = [
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reader')

    # Subscription fields for readers
    subscribed_publishers = models.ManyToManyField(
        'Publisher',
        related_name='subscribers',
        blank=True
    )
    subscribed_journalists = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='subscribers',
        blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Publisher(models.Model):
    """Publisher that can have multiple editors and journalists."""
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    editors = models.ManyToManyField(
        'CustomUser',
        related_name='publisher_editor_of',
        blank=True
    )
    journalists = models.ManyToManyField(
        'CustomUser',
        related_name='publisher_journalist_of',
        blank=True
    )

    def __str__(self):
        return self.name


class Article(models.Model):
    """Article model that can belong to a publisher or be independent."""
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='articles'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)
    publisher = models.ForeignKey(
        'Publisher',
        on_delete=models.SET_NULL,
        related_name='articles',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    """Newsletter containing a collection of articles."""
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    author = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='newsletters'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    articles = models.ManyToManyField(
        'Article',
        related_name='newsletters',
        blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
