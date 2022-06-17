from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class recipes_info(models.Model):
    RecipeId = models.IntegerField(primary_key=True)
    AuthorId = models.IntegerField()
    RecipeServings = models.FloatField(null=True)
    Name = models.TextField(null=True)
    AuthorName = models.TextField(null=True)
    TotalTime = models.TextField(null=True)
    DatePublished = models.TextField(null=True)
    RecipeCategory = models.TextField(null=True)

    def __str__(self):
	    return self.Name

