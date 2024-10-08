# Generated by Django 5.0.6 on 2024-08-14 13:29

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym_app', '0021_workoutschedule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='participants',
            field=models.ManyToManyField(blank=True, related_name='bookings', to=settings.AUTH_USER_MODEL),
        ),
    ]
