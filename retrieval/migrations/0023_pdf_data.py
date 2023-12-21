# Generated by Django 4.2.7 on 2023-12-20 07:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('retrieval', '0022_delete_pdf_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pdf_Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdf1', models.JSONField(blank=True, default=list, null=True)),
                ('pdf3', models.JSONField(blank=True, default=list, null=True)),
                ('pdf2', models.JSONField(blank=True, default=list, null=True)),
                ('pdf4', models.JSONField(blank=True, default=list, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retrieval.company')),
            ],
        ),
    ]