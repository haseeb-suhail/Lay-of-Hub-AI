# Generated by Django 3.2.25 on 2024-09-06 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0046_auto_20240906_0854'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_model',
            name='agreement',
            field=models.BooleanField(default=True),
        ),
    ]
