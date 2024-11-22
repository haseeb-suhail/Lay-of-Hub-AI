# Generated by Django 3.2.25 on 2024-08-07 12:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_notification'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_description', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('admin_or_moderator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.group')),
            ],
        ),
    ]