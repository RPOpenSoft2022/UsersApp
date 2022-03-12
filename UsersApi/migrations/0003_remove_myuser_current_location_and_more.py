# Generated by Django 4.0.3 on 2022-03-11 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UsersApi', '0002_myuser_delete_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myuser',
            name='current_location',
        ),
        migrations.RemoveField(
            model_name='myuser',
            name='last_updated_location',
        ),
        migrations.AddField(
            model_name='myuser',
            name='current_lat',
            field=models.DecimalField(blank=True, decimal_places=16, max_digits=22, null=True, verbose_name='Current Latitude'),
        ),
        migrations.AddField(
            model_name='myuser',
            name='current_long',
            field=models.DecimalField(blank=True, decimal_places=16, max_digits=22, null=True, verbose_name='Current Longitude'),
        ),
        migrations.AddField(
            model_name='myuser',
            name='last_updated_location_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Last updated location time'),
        ),
    ]
