# Generated by Django 4.0.4 on 2022-06-24 08:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_alter_recipes_info_authorname_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='reviews',
            fields=[
                ('ReviewId', models.IntegerField(primary_key=True, serialize=False)),
                ('AuthorId', models.IntegerField()),
                ('AuthorName', models.TextField(null=True)),
                ('Rating', models.IntegerField()),
                ('Review', models.TextField(null=True)),
                ('DateSubmitted', models.TextField(null=True)),
                ('RecipeId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.recipes_info')),
            ],
        ),
    ]