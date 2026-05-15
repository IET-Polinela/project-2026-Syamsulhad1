from django.db import models
from django.conf import settings

STATUS_CHOICES = [
    ('DRAFT', 'Draft'),
    ('REPORTED', 'Reported'),
    ('VERIFIED', 'Verified'),
    ('IN_PROGRESS', 'In Progress'),
    ('RESOLVED', 'Resolved'),
]

CATEGORY_CHOICES = [
    ('INFRASTRUCTURE', 'Infrastruktur & Jalan'),
    ('SECURITY', 'Keamanan'),
    ('HEALTH', 'Kesehatan'),
    ('ENVIRONMENT', 'Lingkungan & Kebersihan'),
    ('PUBLIC_FACILITY', 'Fasilitas Publik'),
]

class Report(models.Model):
    title = models.CharField(max_length=200)

    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        default='ENVIRONMENT'
    )

    description = models.TextField()
    location = models.CharField(max_length=200)

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports',
        null=True,
        blank=True
    )

    is_anonymous = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
