# Generated by Django 2.2 on 2019-04-20 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0012_persoon_selected'),
    ]

    operations = [
        migrations.AddField(
            model_name='persoon',
            name='marked_for_deletion',
            field=models.BooleanField(default=False),
        ),
    ]