# Generated by Django 3.2.25 on 2024-08-02 09:11

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_group_referral_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='group',
            name='referral_url',
        ),
        migrations.AlterField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(blank=True, null=True, related_name='member_groups', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='group',
            name='moderators',
            field=models.ManyToManyField(blank=True, null=True, related_name='moderator_groups', to=settings.AUTH_USER_MODEL),
        ),
    ]
