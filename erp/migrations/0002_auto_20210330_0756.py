# Generated by Django 3.1.7 on 2021-03-30 06:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0001_squashed_0006_auto_20210329_2057'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='delivery_notes',
        ),
        migrations.RemoveField(
            model_name='company',
            name='manufacture_notes',
        ),
        migrations.RemoveField(
            model_name='company',
            name='order_notes',
        ),
    ]
