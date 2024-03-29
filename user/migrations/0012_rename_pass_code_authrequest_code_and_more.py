# Generated by Django 4.0.6 on 2022-07-31 09:33

import datetime
from django.db import migrations, models
import django.utils.timezone
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_alter_authrequest_created_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='authrequest',
            old_name='pass_code',
            new_name='code',
        ),
        migrations.AlterField(
            model_name='authrequest',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='authrequest',
            name='expire_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 31, 9, 35, 46, 422780, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='authrequest',
            name='request_method',
            field=models.CharField(choices=[('not_reg', 'Not Registered'), ('login_pass', 'Login Password'), ('login_code', 'Login Code')], max_length=10),
        ),
    ]
