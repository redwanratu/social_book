# Generated by Django 4.1.5 on 2023-01-19 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='location',
            field=models.TextField(blank=True, max_length=102),
        ),
    ]
