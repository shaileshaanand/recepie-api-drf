# Generated by Django 3.2.3 on 2021-05-22 07:04

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_recepie'),
    ]

    operations = [
        migrations.AddField(
            model_name='recepie',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.recepie_image_file_path),
        ),
    ]
