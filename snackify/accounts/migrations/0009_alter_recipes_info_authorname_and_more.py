# Generated by Django 4.0.4 on 2022-06-20 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_recipes_info_recipeingredientquantities'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipes_info',
            name='AuthorName',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='recipes_info',
            name='Name',
            field=models.CharField(max_length=150, null=True),
        ),
    ]
