# Generated by Django 3.0.1 on 2020-03-13 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0008_auto_20200228_1422'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='attendance',
            field=models.IntegerField(default=0),
        ),
    ]
