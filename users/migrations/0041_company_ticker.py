# Generated by Django 3.2.25 on 2024-09-02 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0040_answer_parent_answer'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='ticker',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
