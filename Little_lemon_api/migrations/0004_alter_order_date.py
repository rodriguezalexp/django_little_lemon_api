# Generated by Django 5.1.5 on 2025-01-29 01:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Little_lemon_api', '0003_alter_cart_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateField(auto_now_add=True, db_index=True),
        ),
    ]
