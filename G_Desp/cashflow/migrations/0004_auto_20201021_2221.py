# Generated by Django 3.1.1 on 2020-10-22 01:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cashflow', '0003_report'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='inflow',
        ),
        migrations.RemoveField(
            model_name='report',
            name='outflow',
        ),
        migrations.RemoveField(
            model_name='report',
            name='value',
        ),
        migrations.AddField(
            model_name='outflow',
            name='billet_code',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='outflow',
            name='payment_code',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='balance',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='balance_percent',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='inflow_values',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='outflow_values',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='description',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='name',
            field=models.CharField(default='Report', max_length=255),
        ),
        migrations.AlterField(
            model_name='report',
            name='registered_by',
            field=models.CharField(max_length=55, null=True),
        ),
    ]
