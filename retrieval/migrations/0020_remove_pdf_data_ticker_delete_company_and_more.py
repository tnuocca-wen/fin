# Generated by Django 4.2.7 on 2023-12-14 11:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('retrieval', '0019_remove_pdf_data_id_alter_pdf_data_ticker'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pdf_data',
            name='ticker',
        ),
        migrations.DeleteModel(
            name='Company',
        ),
        migrations.DeleteModel(
            name='Pdf_Data',
        ),
    ]
