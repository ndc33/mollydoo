# Generated by Django 3.1.5 on 2021-02-26 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0003_auto_20210226_2112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='codename',
            field=models.CharField(max_length=4),
        ),
        migrations.AlterField(
            model_name='company',
            name='shortname',
            field=models.CharField(default='ww', max_length=20),
            preserve_default=False,
        ),
    ]
