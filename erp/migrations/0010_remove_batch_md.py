# Generated by Django 3.1.5 on 2021-03-02 19:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0009_order_container'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='batch',
            name='MD',
        ),
    ]