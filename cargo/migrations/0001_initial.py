# Generated by Django 3.0.3 on 2020-03-01 08:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cargo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Исполнено', 'Исполнено'), ('В пути', 'В пути')], default='В пути', max_length=10, verbose_name='Статус')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Дата поставки')),
            ],
            options={
                'verbose_name': 'Поставка',
                'verbose_name_plural': 'Поставки',
            },
        ),
        migrations.CreateModel(
            name='CargoDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('quantity', models.SmallIntegerField(default=1)),
                ('order_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cargo.Cargo')),
            ],
        ),
    ]