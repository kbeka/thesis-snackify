# Generated by Django 4.0.4 on 2022-06-17 16:49

import birthday.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('birthday_dayofyear_internal', models.PositiveSmallIntegerField(default=None, editable=False, null=True)),
                ('birthday', birthday.fields.BirthdayField()),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('image', models.ImageField(default='default.jpg', upload_to='profile_pics')),
                ('cookbook', models.ManyToManyField(related_name='cook_book', to='accounts.recipes_info')),
                ('favorite', models.ManyToManyField(related_name='fav', to='accounts.recipes_info')),
                ('username', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
