# Generated by Django 4.0.4 on 2022-06-19 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_profile_birthday'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipes_info',
            name='AggregatedRating',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='Calories',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='CarbohydrateContent',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='CholesterolContent',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='CookTime',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='Description',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='FatContent',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='FiberContent',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='Images',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='Keywords',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='NumofRatings',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='PrepTime',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='ProteinContent',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='RecipeIngredientQuantities',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='RecipeInstructions',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='RecipeYield',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='SaturatedFatContent',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='SodiumContent',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='recipes_info',
            name='SugarContent',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='recipes_info',
            name='AuthorName',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='recipes_info',
            name='DatePublished',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='recipes_info',
            name='Name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='recipes_info',
            name='RecipeCategory',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='recipes_info',
            name='TotalTime',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
