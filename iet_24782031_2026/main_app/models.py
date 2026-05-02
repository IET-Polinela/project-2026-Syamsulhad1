from django.db import models

STATUS_CHOICES = [
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
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='REPORTED'
    ) 
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title
