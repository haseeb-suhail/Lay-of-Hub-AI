# Generated by Django 3.2.25 on 2024-09-06 08:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0042_auto_20240903_0910'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='referral',
            name='referral_points',
        ),
        migrations.RemoveField(
            model_name='user_model',
            name='referral_code',
        ),
        migrations.RemoveField(
            model_name='user_model',
            name='referral_points',
        ),
        migrations.RemoveField(
            model_name='user_model',
            name='referred_by',
        ),
    ]
