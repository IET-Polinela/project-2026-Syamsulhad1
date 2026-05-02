# Generated manually for category filter options.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='category',
            field=models.CharField(
                choices=[
                    ('INFRASTRUCTURE', 'Infrastruktur & Jalan'),
                    ('SECURITY', 'Keamanan'),
                    ('HEALTH', 'Kesehatan'),
                    ('ENVIRONMENT', 'Lingkungan & Kebersihan'),
                    ('PUBLIC_FACILITY', 'Fasilitas Publik'),
                ],
                default='ENVIRONMENT',
                max_length=100,
            ),
        ),
    ]
