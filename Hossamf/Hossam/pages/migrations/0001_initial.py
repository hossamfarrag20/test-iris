# Generated by Django 5.0.4 on 2024-05-02 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Npages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('Birth_date', models.DateField()),
                ('phone_number', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=100)),
                ('suger_year', models.IntegerField()),
                ('type_order', models.IntegerField()),
                ('cumulative_glucose_test', models.IntegerField()),
                ('heart_diseases', models.CharField(max_length=100)),
                ('blood_pressure', models.IntegerField()),
                ('cholestrol_level', models.IntegerField()),
                ('smoker', models.CharField(max_length=100)),
                ('Notes', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='photos/%y/%m/%d')),
            ],
        ),
    ]
