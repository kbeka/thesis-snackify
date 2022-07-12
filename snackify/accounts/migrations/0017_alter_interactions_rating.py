# Generated by Django 4.0.4 on 2022-06-26 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_alter_interactions_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interactions',
            name='rating',
            field=models.IntegerField(choices=[(1, '1 - Awful'), (2, '2 - Bad'), (3, '3 - OK'), (4, '4 - Good'), (5, '5 - Awesome')], null=True),
        ),
    ]