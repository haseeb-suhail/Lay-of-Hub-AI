# Generated by Django 3.2.25 on 2024-08-08 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_rename_points_user_model_referral_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='referral',
            name='referral_points',
            field=models.IntegerField(default=0),
        ),
    ]