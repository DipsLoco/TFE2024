# Generated by Django 5.1.2 on 2024-10-29 18:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym_app', '0036_serviceimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceimage',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='serviceimage',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='personalizedcoaching',
            name='coach',
            field=models.ForeignKey(limit_choices_to={'role': 'coach'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
