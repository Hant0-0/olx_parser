# Generated by Django 5.1.4 on 2025-01-12 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parser', '0004_olxad_last_online_seller_olxad_name_seller_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='olxad',
            old_name='imgs_list',
            new_name='images',
        ),
        migrations.AlterField(
            model_name='olxad',
            name='date_published',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
