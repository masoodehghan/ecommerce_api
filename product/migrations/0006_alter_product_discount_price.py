# Generated by Django 4.0.3 on 2022-05-18 11:39

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_product_discount_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='discount_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MaxValueValidator(models.DecimalField(decimal_places=2, max_digits=10))]),
        ),
    ]
