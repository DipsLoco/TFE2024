# Generated by Django 5.0.6 on 2024-08-13 15:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym_app', '0020_plan_is_premium'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkoutSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('coach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scheduled_workouts', to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gym_app.location')),
                ('workout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gym_app.workout')),
            ],
        ),
    ]
