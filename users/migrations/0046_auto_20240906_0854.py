# Generated by Django 3.2.25 on 2024-09-06 08:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0045_auto_20240906_0823'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='referral',
            name='referral_points',
        ),
        migrations.RemoveField(
            model_name='user_model',
            name='referred_by',
        ),
    ]
