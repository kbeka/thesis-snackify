from django.db import models
from django.contrib.auth.models import User
from birthday import BirthdayField
from django.db.models.signals import post_save
from django.dispatch import receiver 
from PIL import Image


# Create your models here.
class recipes_info(models.Model):
    RecipeId = models.IntegerField(primary_key=True)
    Name = models.CharField(max_length=150, null=True)
    AuthorId = models.IntegerField()
    AuthorName = models.CharField(max_length=150, null=True)
    CookTime = models.CharField(max_length=50, null=True)
    PrepTime = models.CharField(max_length=50, null=True)
    TotalTime = models.CharField(max_length=50, null=True)
    DatePublished = models.CharField(max_length=50, null=True)
    Description = models.TextField(null=True)
    Images = models.TextField(null=True)
    RecipeCategory = models.CharField(max_length=50, null=True)
    Keywords = models.TextField(null=True)
    RecipeIngredientQuantities = models.TextField(null=True)
    RecipeIngredientParts = models.TextField(null=True)
    AggregatedRating = models.FloatField(null=True)
    Calories = models.FloatField(null=True)
    FatContent = models.FloatField(null=True)
    SaturatedFatContent = models.FloatField(null=True)
    CholesterolContent = models.FloatField(null=True)
    SodiumContent = models.FloatField(null=True)
    CarbohydrateContent = models.FloatField(null=True)
    FiberContent = models.FloatField(null=True)
    SugarContent = models.FloatField(null=True)
    ProteinContent = models.FloatField(null=True)
    RecipeServings = models.FloatField(null=True)
    RecipeYield = models.CharField(max_length=100, null=True)
    RecipeInstructions = models.TextField(null=True)
    NumofRatings = models.IntegerField(null=True)

    def __str__(self):
	    return self.Name


class reviews(models.Model):
    ReviewId = models.IntegerField(primary_key=True)
    RecipeId = models.ForeignKey(recipes_info , on_delete=models.CASCADE)
    AuthorId = models.IntegerField()
    AuthorName = models.TextField(null=True)
    Rating = models.IntegerField()
    Review = models.TextField(null=True)
    DateSubmitted = models.TextField(null=True)

    def __str__(self):
	    return self.Review

RATE_CHOICES = (
	(1, '1 - Awful'),
	(2, '2 - Bad'),
	(3, '3 - OK'),
	(4, '4 - Really Good'),
	(5, '5 - Amazing'), 
)

class interactions(models.Model):
    #AuthorName = models.ForeignKey(User.username, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    RecipeId = models.ForeignKey(recipes_info , on_delete=models.CASCADE)
    rating = models.IntegerField(choices = RATE_CHOICES, null=True)
    review = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
	    return self.user

class profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    birthday = models.DateField(null=True)
    city = models.CharField(max_length=50,null=True,blank=True)
    date_created = models.DateField(auto_now_add=True)
    cookbook = models.ManyToManyField(recipes_info, related_name="cook_book")
    favorite = models.ManyToManyField(recipes_info, related_name="fav")
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 200 or img.width > 200:
            new_img = (200, 200)
            img.thumbnail(new_img)
            img.save(self.image.path)

    def __str__(self):
	    return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		profile.objects.create(user=instance, first_name = instance.first_name, last_name = instance.last_name, date_created = instance.date_joined)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()


    






