# Generated by Django 4.0.4 on 2022-06-20 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_recipes_info_aggregatedrating_recipes_info_calories_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipes_info',
            name='RecipeIngredientParts',
            field=models.TextField(null=True),
        ),
    ]