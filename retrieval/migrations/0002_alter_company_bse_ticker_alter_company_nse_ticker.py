# Generated by Django 4.2.7 on 2023-11-13 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retrieval', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='bse_ticker',
            field=models.CharField(default='', max_length=15, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='company',
            name='nse_ticker',
            field=models.CharField(default='', max_length=15, null=True),
        ),
    ]
