# Generated by Django 4.2.2 on 2023-06-26 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='image',
            field=models.ImageField(default='static/img/hotel.jpeg', upload_to='static/img'),
        ),
    ]