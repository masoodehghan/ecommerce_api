# Generated by Django 4.1 on 2022-08-12 08:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0017_alter_authrequest_expire_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authrequest',
            name='expire_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 12, 8, 20, 2, 105587, tzinfo=datetime.timezone.utc)),
        ),
    ]