# Generated by Django 3.2.25 on 2024-08-02 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20240802_0834'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='referral_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]