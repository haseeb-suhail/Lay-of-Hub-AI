# Generated by Django 3.2.25 on 2024-08-27 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0038_auto_20240816_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='company_pictures/'),
        ),
    ]