# Generated by Django 3.0.3 on 2020-08-23 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_auto_20200817_0802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
    ]
