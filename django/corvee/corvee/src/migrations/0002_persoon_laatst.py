# Generated by Django 2.1.7 on 2019-04-12 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='persoon',
            name='laatst',
            field=models.DateField(auto_now=True),
        ),
    ]
