# Generated by Django 2.2.3 on 2019-07-16 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20190716_2301'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='citizen',
            name='id',
        ),
        migrations.AlterField(
            model_name='citizen',
            name='citizen_id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
