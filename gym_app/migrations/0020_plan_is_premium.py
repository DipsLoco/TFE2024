# Generated by Django 5.0.6 on 2024-08-12 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym_app', '0019_coach_exp_workout_coachs_workout_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='is_premium',
            field=models.BooleanField(default=False),
        ),
    ]
