# Generated by Django 4.0.6 on 2022-07-31 09:33

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0009_alter_order_delivery_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateField(default=datetime.date(2022, 8, 4), validators=[django.core.validators.MinValueValidator(datetime.date(2022, 8, 3))]),
        ),
    ]
