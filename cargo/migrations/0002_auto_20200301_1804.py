# Generated by Django 3.0.3 on 2020-03-01 08:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('warehouse', '0001_initial'),
        ('common', '0001_initial'),
        ('cargo', '0001_initial'),
        ('supplier', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cargo',
            name='stocks',
            field=models.ManyToManyField(through='common.CargoStock', to='warehouse.Stock', verbose_name='Товары'),
        ),
        migrations.AddField(
            model_name='cargo',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supplier.Supplier', verbose_name='Поставщик'),
        ),
    ]
