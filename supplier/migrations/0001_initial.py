# Generated by Django 3.0.3 on 2020-03-01 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('category', '0001_initial'),
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization', models.CharField(max_length=80, verbose_name='Организация')),
                ('address', models.TextField(verbose_name='Адрес')),
                ('phone_number', models.CharField(max_length=20, verbose_name='Телефон')),
                ('email', models.EmailField(max_length=254, verbose_name='Электронная почта')),
                ('legal_details', models.TextField(verbose_name='Реквизиты')),
                ('contact_info', models.TextField(null=True, verbose_name='Контактная информация')),
                ('categories', models.ManyToManyField(through='common.SupplierCategory', to='category.Category')),
            ],
            options={
                'verbose_name': 'Поставщик',
                'verbose_name_plural': 'Поставщики',
            },
        ),
    ]
