# Generated by Django 4.2.13 on 2024-09-10 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0009_npages_heart_status_npages_smoker_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='npages',
            name='image',
            field=models.FileField(upload_to='modelphoto'),
        ),
    ]
