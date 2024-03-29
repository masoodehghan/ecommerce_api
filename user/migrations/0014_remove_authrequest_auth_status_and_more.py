# Generated by Django 4.0.6 on 2022-08-01 08:37

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_rename_request_method_authrequest_auth_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='authrequest',
            name='auth_status',
        ),
        migrations.RemoveField(
            model_name='authrequest',
            name='code',
        ),
        migrations.AddField(
            model_name='authrequest',
            name='pass_code',
            field=models.CharField(blank=True, max_length=5),
        ),
        migrations.AddField(
            model_name='authrequest',
            name='request_method',
            field=models.CharField(choices=[('not_reg', 'Not Registered'), ('pass_login', 'Password Login'), ('code_login', 'Code Login')], default=datetime.datetime(2022, 8, 1, 8, 37, 17, 392055, tzinfo=utc), max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='authrequest',
            name='expire_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 1, 8, 39, 8, 290322, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='authrequest',
            name='modified',
            field=models.DateTimeField(),
        ),
    ]
