# Generated by Django 3.2.23 on 2024-01-17 00:08

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_fooditem_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fooditem',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.food_item_image_file_path),
        ),
    ]