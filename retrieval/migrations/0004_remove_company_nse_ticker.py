# Generated by Django 4.2.7 on 2023-11-13 13:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('retrieval', '0003_remove_company_moq'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='nse_ticker',
        ),
    ]
