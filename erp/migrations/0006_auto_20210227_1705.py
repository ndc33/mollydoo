# Generated by Django 3.1.5 on 2021-02-27 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0005_auto_20210227_1403'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MPrintOrder',
        ),
        migrations.DeleteModel(
            name='WorksTestPrintOrder',
        ),
        migrations.CreateModel(
            name='WorkCutView',
            fields=[
            ],
            options={
                'verbose_name_plural': 'Works Cut View',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('erp.order',),
        ),
        migrations.CreateModel(
            name='WorkPrintView',
            fields=[
            ],
            options={
                'verbose_name_plural': 'Works Print View',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('erp.order',),
        ),
        migrations.RenameField(
            model_name='order',
            old_name='delivery_notes',
            new_name='xdelivery_notes',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='manufacture_notes',
            new_name='xmanufacture_notes',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='order_notes',
            new_name='xorder_notes',
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='cutx',
            field=models.BooleanField(default=False, verbose_name='cut'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='tally_cut',
            field=models.CharField(blank=True, default='', max_length=120, verbose_name='tally'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='tally_pack',
            field=models.CharField(blank=True, default='', max_length=120, verbose_name='tally'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='tally_print',
            field=models.CharField(blank=True, default='', max_length=120, verbose_name='tally'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='tally_stuff',
            field=models.CharField(blank=True, default='', max_length=120, verbose_name='tally'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='tally_weld',
            field=models.CharField(blank=True, default='', max_length=120, verbose_name='tally'),
        ),
    ]