# Generated by Django 3.2.8 on 2021-10-28 08:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('abs_app', '0002_application_token'),
    ]

    operations = [
        migrations.RenameField(
            model_name='version',
            old_name='application_id',
            new_name='application_token',
        ),
    ]
