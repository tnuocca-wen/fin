# Generated by Django 4.2.7 on 2023-12-13 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retrieval', '0007_alter_company_company_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='company_name',
            field=models.CharField(max_length=1000),
        ),
    ]
