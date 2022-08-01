# Generated by Django 4.0.6 on 2022-08-01 08:42

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_remove_authrequest_auth_status_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='authrequest',
            old_name='request_method',
            new_name='auth_status',
        ),
        migrations.RenameField(
            model_name='authrequest',
            old_name='pass_code',
            new_name='code',
        ),
        migrations.AlterField(
            model_name='authrequest',
            name='expire_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 1, 8, 44, 16, 762041, tzinfo=utc)),
        ),
    ]