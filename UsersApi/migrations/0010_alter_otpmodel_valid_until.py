# Generated by Django 4.0.3 on 2022-03-12 14:26

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('UsersApi', '0009_myuser_is_free_alter_otpmodel_valid_until'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otpmodel',
            name='valid_until',
            field=models.DateTimeField(default=datetime.datetime(2022, 3, 12, 14, 31, 28, 341143, tzinfo=utc), help_text='The timestamp of the moment of expiry of the saved token.'),
        ),
    ]
