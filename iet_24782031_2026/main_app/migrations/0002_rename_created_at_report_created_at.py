
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='report',
            old_name='Created_at',
            new_name='created_at',
        ),
    ]
