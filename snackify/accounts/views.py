from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import recipes_info,reviews,profile, interactions
from .forms import *
from django.template import loader
import pandas as pd
import numpy as np
import json
import itertools
import random

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

from surprise import BaselineOnly
from surprise import Dataset, accuracy, Reader

def top_recipes(request):
    recipes_home = pd.DataFrame(list(recipes_info.objects.all().values()))
    reviews_home = pd.DataFrame(list(reviews.objects.all().values()))

    reviews_home = reviews_home[['RecipeId_id', 'Rating']]

    #Store average rating of meals
    C=reviews_home['Rating'].mean()

    #Group seperate meal ratings together and get average meal score equally prevent recipe_id from being an index
    reviews_home = reviews_home.groupby(['RecipeId_id'])['Rating'].agg(['mean','count'])
    reviews_home.reset_index(inplace=True)

    #Rename columns 
    reviews_home.rename(columns={'mean':'average_rating','count':'votes'},inplace=True)

    #Merge ratings dataframe with recipe Dataframe
    food_df = pd.merge(recipes_home, reviews_home, left_on='RecipeId',right_on='RecipeId_id')

    #Show the number of votes possesed by the top 10% meals, based on number of votes
    q=reviews_home['votes'].quantile(0.9)

    #Get meals which have received a substantial number of votes
    top_meals=food_df.copy().loc[reviews_home['votes']>=q]

    #This function permits us to compute a special metric which takes into account the number of people
    #that have voted for a meal and not just it's average rating
    def weighted_rating(x, m=q, c=C):
        v = x['votes']
        R = x['average_rating']
        return (v/(v+m) * R) + (m/(m+v) * C)

    #Select top meals from Dataframe
    top_meals['Score']=top_meals.apply(weighted_rating, axis=1)
    food_df['Score']=food_df.apply(weighted_rating, axis=1)

    #Sort best meals based on their scores
    top_meals=top_meals.sort_values('Score',ascending=False)
    top_meals = top_meals[top_meals.Score > 4.68]
    top_meals.Images = top_meals.Images.str[2:-2]
    top_meals.Images = top_meals.Images.str.split("'").str[0]
    
    
    json_records = top_meals.reset_index().to_json(orient ='records')
    data = []
    data = json.loads(json_records)
    context = {'d': data}

    return(context)

def home(request):
    context = top_recipes(request)

    return render(request, 'home.html', context)

#### RECIPE INFORMATION PAGE ####

def recipe_page(request, RecipeId):
    recipe_data = recipes_info.objects.get(RecipeId = RecipeId)
    reviews_data = reviews.objects.filter(RecipeId = RecipeId)
    reviews_data = reviews_data.order_by('-DateSubmitted')
    our_reviews = interactions.objects.filter(RecipeId = recipe_data).exclude(review__isnull=True).exclude(user=request.user)
    our_reviews = our_reviews.order_by('-date')

    
    #user's review
    user_review = interactions.objects.filter(user=request.user).filter(RecipeId = recipe_data).exclude(review__isnull=True).first()

    # list of images
    recipe_data.Images = recipe_data.Images[2:-2]
    image_list = recipe_data.Images.split("', '")

    #list of instructions
    recipe_data.RecipeInstructions = recipe_data.RecipeInstructions[2:-2]
    instructions_list = recipe_data.RecipeInstructions.split("', '")

    #list of ingredient quantities
    recipe_data.RecipeIngredientQuantities = recipe_data.RecipeIngredientQuantities[2:-2]
    ingr_quant_list = recipe_data.RecipeIngredientQuantities.split("', '") 

    #list of ingredient parts
    recipe_data.RecipeIngredientParts = recipe_data.RecipeIngredientParts[2:-2]
    ingr_part_list = recipe_data.RecipeIngredientParts.split("', '")   

    #ziped
    ingr_list = zip(ingr_quant_list, ingr_part_list)


    user = request.user
    user_prof = profile.objects.get(user=user)
    favorite = profile.objects.filter(user=user).filter(favorite = RecipeId).exists()

    cookbook = profile.objects.filter(user=user).filter(cookbook = RecipeId).exists()

    if_rate = False
    if_review = False
    rate = -1
    review = -1

    rating_num = -1

    if (if_rated(request, RecipeId)):
        if_rate = True
        rate = rating_instance(request, RecipeId)
        rating_num = rate.rating
    else:
        if_rate = False

    if (if_reviewed(request, RecipeId)):
        review = review_instance(request, RecipeId)
        if_review = True
    else:
        if_review = False
    # form for rating recipes 

    if request.method == 'POST' and 'rate_recipe'  in request.POST:
        form2 = ReviewForm()
        if(if_rate):
            form1 = RatingForm(request.POST, instance = rate)
        elif(if_review):
            form1 = RatingForm(request.POST, instance = review)
        else:
            form1 = RatingForm(request.POST)
        if form1.is_valid():
            rate = form1.save(commit=False)
            rate.user = user
            rate.RecipeId = recipe_data
            rate.save()
            return HttpResponseRedirect(reverse('recipe_page', args=[RecipeId]))
    elif request.method == 'POST' and 'review_recipe'  in request.POST:
        form1 = RatingForm()
        if(if_rate):
            form2 = ReviewForm(request.POST, instance = rate)
        elif(if_review):
            form2 = RatingForm(request.POST, instance = review)
        else:
            form2 = ReviewForm(request.POST)
        if form2.is_valid():
            review = form2.save(commit=False)
            review.user = user
            review.RecipeId = recipe_data
            review.save()
            return HttpResponseRedirect(reverse('recipe_page', args=[RecipeId]))
    else:
            form1 = RatingForm()
            form2 = ReviewForm()
    
    
    context = {'recipe': recipe_data, 'reviews': reviews_data, 'our_reviews': our_reviews,'recipe_images': image_list, 
    'instruction_list': instructions_list, 'ingr_quant_list': ingr_quant_list, 'ingr_part_list': ingr_part_list, 'ingr_list': ingr_list, 'favorite': favorite, 'cookbook': cookbook, 'form1': form1, 'form2': form2, 
    'if_rated': if_rate, 'if_reviewed': if_review, 'user_review': user_review, 'rating': rating_num}

    return render(request, 'recipe_information.html', context)
    

def if_rated(request, RecipeId):
    recipe = recipes_info.objects.get(RecipeId = RecipeId)
    user = request.user
    rate = interactions.objects.filter(user = user).filter(RecipeId = recipe).exists()
    if(rate):
        rate = interactions.objects.filter(user = user).filter(RecipeId = recipe).first()
        if(rate.rating is None):
            return (False)
        return(True)
    return(False)

def rating_instance(request, RecipeId):
    recipe = recipes_info.objects.get(RecipeId = RecipeId)
    user = request.user
    rate = interactions.objects.filter(user = user).filter(RecipeId = recipe).first()
    if(rate.rating is None):
        return (-1)
    return(rate)

def if_reviewed(request, RecipeId):
    recipe = recipes_info.objects.get(RecipeId = RecipeId)
    user = request.user
    review = interactions.objects.filter(user = user).filter(RecipeId = recipe).exists()
    if(review):
        review = interactions.objects.filter(user = user).filter(RecipeId = recipe).first()
        if(review.review is None):
            return (False)
        return(True)
    return(False)

def review_instance(request, RecipeId):
    recipe = recipes_info.objects.get(RecipeId = RecipeId)
    user = request.user
    review = interactions.objects.filter(user = user).filter(RecipeId = recipe).first()
    if(review.review is None):
        return (-1)
    return(review)

def remove_favorite(request, RecipeId):
    user = request.user
    user_prof = profile.objects.get(user = user)
    recipe = recipes_info.objects.get(RecipeId = RecipeId)
    user_prof.favorite.remove(recipe)

    return HttpResponseRedirect(reverse('recipe_page', args=[RecipeId]))

def remove_cookbook(request, RecipeId):
    user = request.user
    user_prof = profile.objects.get(user = user)
    recipe = recipes_info.objects.get(RecipeId = RecipeId)
    user_prof.cookbook.remove(recipe)

    return HttpResponseRedirect(reverse('recipe_page', args=[RecipeId]))

def add_favorite(request, RecipeId):
    user = request.user
    user_prof = profile.objects.get(user = user)
    recipe = recipes_info.objects.get(RecipeId = RecipeId)
    user_prof.favorite.add(recipe)

    return HttpResponseRedirect(reverse('recipe_page', args=[RecipeId]))

def add_cookbook(request, RecipeId):
    user = request.user
    user_prof = profile.objects.get(user = user)
    recipe = recipes_info.objects.get(RecipeId = RecipeId)
    user_prof.cookbook.add(recipe)

    return HttpResponseRedirect(reverse('recipe_page', args=[RecipeId]))

def delete_review(request, RecipeId):
    recipe_data = recipes_info.objects.get(RecipeId = RecipeId)
    user_review = interactions.objects.filter(user=request.user).filter(RecipeId = recipe_data).first()
    user_review.review = None
    if(user_review.rating is None):
        user_review.delete()
    else:
        user_review.save()
    
    return HttpResponseRedirect(reverse('recipe_page', args=[RecipeId]))


#### END RECIPE INFORMATION PAGE ####

#### PROFILE INFORMATION PAGE ####

def profile_info(request, username):
    user_prof = profile.objects.get(user_id=request.user)
    user_reviews = interactions.objects.filter(user = request.user).exclude(review__isnull = True)
    
    user_cookbook = pd.DataFrame(list(user_prof.cookbook.all().values()))
    if(user_cookbook.empty == False):
        user_cookbook.Images = user_cookbook.Images.str[2:-2]
        user_cookbook.Images = user_cookbook.Images.str.split("'").str[0]

    if(len(user_cookbook)>3):
        user_cookbook = user_cookbook.head(3)

    json_records = user_cookbook.reset_index().to_json(orient ='records')
    data = []
    cookbook = json.loads(json_records)

    user_favorite = pd.DataFrame(list(user_prof.favorite.all().values()))
    if(user_favorite.empty == False):
        user_favorite.Images = user_favorite.Images.str[2:-2]
        user_favorite.Images = user_favorite.Images.str.split("'").str[0]

    if(len(user_favorite)>3):
        user_favorite = user_favorite.head(3)

    json_records = user_favorite.reset_index().to_json(orient ='records')
    data = []
    favorite = json.loads(json_records)

    return render(request, 'profile.html', {'user_prof':user_prof, 'user_cookbook': cookbook, 'user_favorite': favorite,
    'user_review': user_reviews})

@login_required
def edit_profile(request, username):
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)  # request.FILES is show the selected image or file

        if form.is_valid() and profile_form.is_valid():
            user_form = form.save()
            custom_form = profile_form.save(False)
            custom_form.user = user_form
            custom_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return HttpResponseRedirect(reverse('edit_profile', args=[request.user.username]))
    else:
        form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)
        args = {}
        # args.update(csrf(request))
        args['form'] = form
        args['profile_form'] = profile_form
        return render(request, 'edit_profile.html', args)

@login_required
def change_password(request, username):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect(reverse('edit_profile', args=[request.user.username]))
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })

#### END PROFILE INFORMATION PAGE ####

### CATEGORIES ###

def categories_page(request):
    if request.method == "POST":
        category = request.POST.get('categ')
        return category_recipes(request, category)
    categories = pd.DataFrame(list(recipes_info.objects.all().values()))
    categ = categories.RecipeCategory.unique()
    categ = np.sort(categ)
    # categ = pd.DataFrame(categ, columns=['categories'])


    page = request.GET.get('page', 1)
    paginator = Paginator(categ, 20)
    page_range = paginator.get_elided_page_range(number=page)

    try:
        category = paginator.page(page)
    except PageNotAnInteger:
        category = paginator.page(1)
    except EmptyPage:
        category = paginator.page(paginator.num_pages)

    return render(request, 'categories_page.html', {'category': category, 'categories': categ, 'page_range': page_range})

def category_recipes(request, category):
    rec_cat = recipes_info.objects.filter(RecipeCategory = category)
    recipes = pd.DataFrame(list(rec_cat.all().values()))
    
    num_of_recipes = recipes.shape[0]

    recipes.Images = recipes.Images.str[2:-2]
    recipes.Images = recipes.Images.str.split("'").str[0]

    json_records = recipes.reset_index().to_json(orient ='records')
    data = []
    recipes_data = json.loads(json_records)

    page = request.GET.get('page', 1)
    paginator = Paginator(recipes_data, 20)
    page_range = paginator.get_elided_page_range(number=page)

    try:
        recipes_data = paginator.page(page)
    except PageNotAnInteger:
        recipes_data = paginator.page(1)
    except EmptyPage:
        recipes_data = paginator.page(paginator.num_pages)
    
    return render(request, 'category_recipes.html', {'recipes': recipes_data, 'num_of_recipes': num_of_recipes, 'page_range': page_range})
    
### END CATEGORIES ###

### SEARCH OPTIONS ###

def nutrition_page(request):
    recipes = pd.DataFrame(list(recipes_info.objects.all().values()))

   
    return render(request, 'nutrition_page.html')

def nutrition_recipes(request):
    message = True
    recipes_data = False

    if request.method == 'GET':
        recipe = request.GET.get('nutr')
    # if recipe == '':
    #     recipe = 'None'

    if(recipe == 'None'):
        message = False
    else:
        recipes = pd.DataFrame(list(recipes_info.objects.all().values()))
        recipes = recipes.drop_duplicates(subset=['Name'])

        if(recipe not in recipes.Name.values):
            message = False
            return render(request, 'nutrition_recipes.html', {'recipes': recipes_data, 'message': message, 'recipe': recipe})

        nutrition = recipes[['Name', 'FatContent', 'SaturatedFatContent', 'CholesterolContent', 'SodiumContent', 
                        'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent']]

        cal = nutrition.pivot_table(columns='Name',values=['FatContent','SaturatedFatContent','CholesterolContent','SodiumContent',
        'CarbohydrateContent', 'FiberContent', 'SugarContent', 'ProteinContent'])

        results = predict(cal, recipe)
        
        if(bool(results)):
            # print(results)
            recipes = pd.DataFrame(list(recipes_info.objects.all().values()))
            data = pd.DataFrame(columns = list(recipes.columns.values))

            for i in results:
                new = recipes.loc[recipes['Name'] == i]
                print(new)
                data = pd.concat([data, new])
                
            data.Images = data.Images.str[2:-2]
            data.Images = data.Images.str.split("'").str[0]
            

            json_records = data.reset_index().to_json(orient ='records')
            data = []
            recipes_data = json.loads(json_records)
        else:
            message = False
        
        num_of_recipes = len(results)

        page = request.GET.get('page', 1)
        paginator = Paginator(recipes_data, 20)
        page_range = paginator.get_elided_page_range(number=page)

        try:
            recipes_data = paginator.page(page)
        except PageNotAnInteger:
            recipes_data = paginator.page(1)
        except EmptyPage:
            recipes_data = paginator.page(paginator.num_pages)
       

    return render(request, 'nutrition_recipes.html', {'recipes': recipes_data, 'page_range': page_range, 'num_of_recipes': num_of_recipes, 'message': message, 'recipe': recipe})


def predict(cal, recipe_name, correl = 0.999, recipe_number = 201):
    nutrition_recipe = cal[recipe_name]
    
#   find similar recipes
    similar = cal.corrwith(nutrition_recipe)
    corr = pd.DataFrame(similar, columns=['Correlation'])
    corr = corr[corr['Correlation'] > correl]
    corr.dropna(inplace=True)
    
    # sort by correlation
    corr = corr.sort_values('Correlation', ascending=False)
    return(corr.iloc[1:recipe_number, :].index.to_list())

### END SEARCH OPTIONS ###

### INGEDIENTS ###

def ingredient_recipes(request, ingredients):
    recipes = pd.DataFrame(list(recipes_info.objects.all().values()))

    

    if request.method == 'GET':
        ingredient = request.GET.get('ingredients')
        if ingredient == '':
            ingredient = 'None'

    if(ingredient == None):
        ingred = list(ingredients.split(","))
    else:
        ingredients = ingredient
        ingred = list(ingredient.split(","))
    
    data = score_recipes(ingred, recipes)
    data.Images = data.Images.str[2:-2]
    data.Images = data.Images.str.split("'").str[0]

    # num_of_recipes = np.shape(data)
    num_of_recipes = len(data)

    json_records = data.reset_index().to_json(orient ='records')
    data = []
    recipes_data = json.loads(json_records)

    page = request.GET.get('page', 1)
    paginator = Paginator(recipes_data, 20)
    page_range = paginator.get_elided_page_range(number=page)

    try:
        recipes_data = paginator.page(page)
    except PageNotAnInteger:
        recipes_data = paginator.page(1)
    except EmptyPage:
        recipes_data = paginator.page(paginator.num_pages)
    
    

    return render(request, 'ingredient_recipes.html', {'recipes': recipes_data, 'num_of_recipes': num_of_recipes, 'ingredient': ingredients, 'page_range': page_range})

def score_recipes(user_input, df):
    '''
    user_input: list of strings
    df: our list of recipes
    best_num: number of best matching result to return
    '''
    df = df.copy()

    def score(ingredient_list):
        
        score = 0
        for w in user_input:
            if w in ingredient_list:
                score += 1
        return score

    df['score'] = df['RecipeIngredientParts'].apply(lambda x: score(x))
    df = df.sort_values(by='score', ascending=False).iloc[:]
    return df[df.score > 0]

def ingredients_page(request):
    recipes = pd.DataFrame(list(recipes_info.objects.all().values()))


    recipes_pasta = score_recipes(list('pasta'.split(",")), recipes).head(4)
    recipes_chicken = score_recipes(list('chicken'.split(",")), recipes).head(4)
    recipes_dough = score_recipes(list('dough'.split(",")), recipes).head(4)
    recipes_chocolate = score_recipes(list('chocolate'.split(",")), recipes).head(4)
    ingr1 = 'pasta'
    ingr2 = 'chicken'
    ingr3 = 'dough'
    ingr4 = 'chocolate'

    recipes_pasta.Images = recipes_pasta.Images.str[2:-2]
    recipes_pasta.Images = recipes_pasta.Images.str.split("'").str[0]

    json_records1 = recipes_pasta.reset_index().to_json(orient ='records')
    data = []
    pasta = json.loads(json_records1)
    
    recipes_chicken.Images = recipes_chicken.Images.str[2:-2]
    recipes_chicken.Images = recipes_chicken.Images.str.split("'").str[0]

    json_records2 = recipes_chicken.reset_index().to_json(orient ='records')
    data = []
    chicken = json.loads(json_records2)

    recipes_dough.Images = recipes_dough.Images.str[2:-2]
    recipes_dough.Images = recipes_dough.Images.str.split("'").str[0]

    json_records3 = recipes_dough.reset_index().to_json(orient ='records')
    data = []
    dough = json.loads(json_records3)

    recipes_chocolate.Images = recipes_chocolate.Images.str[2:-2]
    recipes_chocolate.Images = recipes_chocolate.Images.str.split("'").str[0]

    json_records4 = recipes_chocolate.reset_index().to_json(orient ='records')
    data = []
    chocolate = json.loads(json_records4)

    return render(request, 'ingredients_page.html', {'pasta': pasta, 'chicken': chicken, 'dough': dough, 'chocolate': chocolate, 
    'ingr1': ingr1, 'ingr2': ingr2, 'ingr3': ingr3, 'ingr4': ingr4})

### END INGEDIENTS ###

### SEARCH BY NAME OR CATEGORY ###

def search(request):
    search_request = 'None'
    if request.method == 'GET':
        search_request = request.GET.get('search')
        if search_request == '':
            search_request = 'None'
            message = False
            return render(request, 'search_results.html', { 'message': message, 'search_request': search_request})
            

    recipes_name = pd.DataFrame(list(recipes_info.objects.filter(Q(Name__contains = search_request)).values()))
    recipes_category = pd.DataFrame(list(recipes_info.objects.filter(Q(RecipeCategory__contains = search_request)).values()))
    if(recipes_name.empty == False):
        recipes_name.Images = recipes_name.Images.str[2:-2]
        recipes_name.Images = recipes_name.Images.str.split("'").str[0]

    json_records = recipes_name.reset_index().to_json(orient ='records')
    data = []
    recipes_name_data = json.loads(json_records)

    if(recipes_category.empty == False):
        recipes_category.Images = recipes_category.Images.str[2:-2]
        recipes_category.Images = recipes_category.Images.str.split("'").str[0]

    json_records = recipes_category.reset_index().to_json(orient ='records')
    data = []
    recipes_category_data = json.loads(json_records)

    message = True
    if(recipes_category.empty and recipes_name.empty):
        message = False


    return render(request, 'search_results.html', {'recipes_name': recipes_name_data, 'recipes_category': recipes_category_data, 'message': message, 'search_request': search_request})


### END SEARCH BY NAME OR CATEGORY ###


def cookbook(request, username):
    user_prof = profile.objects.get(user_id = request.user)

    user_cookbook = pd.DataFrame(list(user_prof.cookbook.all().values()))
    user_cookbook.Images = user_cookbook.Images.str[2:-2]
    user_cookbook.Images = user_cookbook.Images.str.split("'").str[0]

    json_records = user_cookbook.reset_index().to_json(orient ='records')
    data = []
    cookbook = json.loads(json_records)

    return render(request, 'cookbook.html', {'user_prof':user_prof, 'user_cookbook': cookbook})

def favorite(request, username):
    user_prof = profile.objects.get(user_id = request.user)
    
    user_favorite = pd.DataFrame(list(user_prof.favorite.all().values()))
    user_favorite.Images = user_favorite.Images.str[2:-2]
    user_favorite.Images = user_favorite.Images.str.split("'").str[0]

    json_records = user_favorite.reset_index().to_json(orient ='records')
    data = []
    favorite = json.loads(json_records)

    return render(request, 'favorite.html', {'user_prof':user_prof, 'user_favorite': favorite})

def recipes_other_user(request, username):
    user_prof = profile.objects.get(user_id = request.user)
    
    user_favorite = pd.DataFrame(list(user_prof.favorite.all().values()))
    user_favorite.Images = user_favorite.Images.str[2:-2]
    user_favorite.Images = user_favorite.Images.str.split("'").str[0]

    json_records = user_favorite.reset_index().to_json(orient ='records')
    data = []
    favorite = json.loads(json_records)

    return render(request, 'recipes_other_user.html', {'user_prof':user_prof, 'recipes': recipes_other_user})

def about_us(request):
    return render(request, 'about_us.html')

def volume_conv(request):
    return render(request, 'volume_conv.html')

def length_conv(request):
    return render(request, 'length_conv.html')

def temperature_conv(request):
    return render(request, 'temperature_conv.html')

def other_profile_info(request, AuthorName):

    user_prof = False
    cookbook = False
    favorite = False
    user_name = AuthorName
    user_reviews2 = False

    if User.objects.filter(username=AuthorName).exists():
        
        user_id = User.objects.get(username = AuthorName).pk
        if(AuthorName == request.user):
            return profile(request, AuthorName)
        user_prof = profile.objects.get(user_id = user_id)
        user_reviews2 = interactions.objects.filter(user = user_id).exclude(review__isnull = True)
        
        user_cookbook = pd.DataFrame(list(user_prof.cookbook.all().values()))
        if(user_cookbook.empty == False):
            user_cookbook.Images = user_cookbook.Images.str[2:-2]
            user_cookbook.Images = user_cookbook.Images.str.split("'").str[0]

        if(len(user_cookbook)>3):
            user_cookbook = user_cookbook.head(3)

        json_records = user_cookbook.reset_index().to_json(orient ='records')
        data = []
        cookbook = json.loads(json_records)

        user_favorite = pd.DataFrame(list(user_prof.favorite.all().values()))
        if(user_favorite.empty == False):
            user_favorite.Images = user_favorite.Images.str[2:-2]
            user_favorite.Images = user_favorite.Images.str.split("'").str[0]

        if(len(user_favorite)>3):
            user_favorite = user_favorite.head(3)

        json_records = user_favorite.reset_index().to_json(orient ='records')
        data = []
        favorite = json.loads(json_records)

    recipes_user = pd.DataFrame(list(recipes_info.objects.filter(AuthorName = AuthorName).values()))
    recipes_user_data = False

    if(not recipes_user.empty):
        recipes_user.Images = recipes_user.Images.str[2:-2]
        recipes_user.Images = recipes_user.Images.str.split("'").str[0]

        if(len(recipes_user)>3):
            recipes_user = recipes_user.head(3)

        json_records = recipes_user.reset_index().to_json(orient ='records')
        data = []
        recipes_user_data = json.loads(json_records)

    user_reviews1 = reviews.objects.filter(AuthorName = AuthorName)
    
    

    return render(request, 'other_profile.html', {'user_prof':user_prof, 'user_cookbook': cookbook, 'user_favorite': favorite,
    'user_reviews1': user_reviews1, 'user_reviews2': user_reviews2, 'user_name': user_name, 'recipes': recipes_user_data})

    return render(request, 'other_profile.html')

def more_recipes(request, AuthorName):
    if User.objects.filter(username=AuthorName).exists():
        return 
    recipes_user = pd.DataFrame(list(recipes_info.objects.filter(AuthorName = AuthorName).values()))
    recipes_user_data = False

    if(not recipes_user.empty):
        recipes_user.Images = recipes_user.Images.str[2:-2]
        recipes_user.Images = recipes_user.Images.str.split("'").str[0]

        json_records = recipes_user.reset_index().to_json(orient ='records')
        data = []
        recipes_user_data = json.loads(json_records)

    return render(request, 'recipes_other_user.html', {'recipes': recipes_user_data, 'username': AuthorName})

def more_favorite(request, AuthorName):
    if User.objects.filter(username=AuthorName).exists():
        user_id = User.objects.get(username = AuthorName).pk
        user_prof = profile.objects.get(user_id = user_id)
        
        user_favorite = pd.DataFrame(list(user_prof.favorite.all().values()))
        user_favorite.Images = user_favorite.Images.str[2:-2]
        user_favorite.Images = user_favorite.Images.str.split("'").str[0]

        json_records = user_favorite.reset_index().to_json(orient ='records')
        data = []
        favorite = json.loads(json_records)

        return render(request, 'favorite.html', {'user_prof':user_prof, 'user_favorite': favorite})
    else:
        return
    

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password==confirm_password:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username is already taken')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email is already taken')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, password=password, 
                                        email=email, first_name=first_name, last_name=last_name)
                user.save()
                
                return redirect('login')


        else:
            messages.info(request, 'Both passwords are not matching')
            return redirect(register)
            

    else:
        return render(request, 'registration/registration.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Invalid Username or Password')
            return redirect('login')



    else:
        return render(request, 'registration/login.html')

def logout(request):
    auth.logout(request)
    return redirect('home')

def all_recipes(request):
    Name = recipes_info.objects.all
    return render(request, 'recipes.html', 
    {'Name': Name})


def recommedation_system(request):

    ### CONTENT-BASED

    recommendations = False
    name = False
    message = False
    recipe_name = False
    user_prof = profile.objects.get(user = request.user)
    cos_sim_res= []
    recipes = pd.DataFrame(list(recipes_info.objects.all().values()))

    user_favorite = pd.DataFrame(list(user_prof.favorite.all().values()))
    if(user_favorite.empty == False):
        df_len = len(user_favorite)
        recipes_name = []
        for i in range(df_len):
            recipes_name.append(user_favorite['Name'][i])

        df_recipes = pd.read_csv(r'C:\Users\alkis\OneDrive\Υπολογιστής\ΤΗΜΜΥ\ΔΙΠΛΩΜΑΤΙΚΗ\csv\content_based.csv')

        cv = CountVectorizer(analyzer='word',strip_accents='unicode',stop_words='english')
        count_matrix = cv.fit_transform(df_recipes['total_parsed'])

        cosine_sim = cosine_similarity(count_matrix,count_matrix)

        df_recipes.reset_index(inplace=True,drop=True)

        

        def get_id_from_index(index):
            return df_recipes[df_recipes.index == index]["RecipeId"].values[0]

        

        for recipe_name in recipes_name:

            recipe_index = df_recipes[df_recipes['Name'] == recipe_name].index.values[0]

            similar_recipes = list(enumerate(cosine_sim[recipe_index]))

            sorted_similar_recipe = sorted(similar_recipes, key=lambda x:x[1], reverse=True)

            j = 0
            for i in sorted_similar_recipe[1:]:
                cos_sim_res.append(get_id_from_index(i[0]))
                j = j+1
                if j >20:
                    break

    ### COLLABORATIVE FILTERING

    df1 = pd.DataFrame(list(reviews.objects.all().values()))
    df2 = pd.DataFrame(list(interactions.objects.all().values()))
    df2 = df2.dropna(axis=0,subset=['rating'])

    df1 = df1[['AuthorId', 'RecipeId_id', 'Rating']]
    df1 = df1.rename(columns = {'AuthorId': 'UserId', 'RecipeId_id': 'RecipeId'})

    df2 = df2[['user_id', 'RecipeId_id', 'rating']]
    df2 = df2.rename(columns = {'user_id': 'UserId', 'rating': 'Rating', 'RecipeId_id': 'RecipeId'})

    df_colab = pd.concat([df1,df2])

    #To reduce the dimensionality of the data set avoiding any "memory error", rarely rated repices and rarely rating users will be removed.

    min_recipe_ratings = 20
    filter_recipes = df_colab['RecipeId'].value_counts() > min_recipe_ratings
    filter_recipes = filter_recipes[filter_recipes].index.tolist()

    min_user_ratings = 1
    filter_users = df_colab['UserId'].value_counts() > min_user_ratings
    filter_users = filter_users[filter_users].index.tolist()

    df_new = df_colab[(df_colab['RecipeId'].isin(filter_recipes)) & (df_colab['UserId'].isin(filter_users))]

    if(request.user.id in df_new['UserId'].values):
        reader = Reader()
        data = Dataset.load_from_df(df_new[['UserId', 'RecipeId', 'Rating']], reader)

        bsl_options = {'method': 'als',
                'n_epochs': 5,
                'reg_u': 12,
                'reg_i': 5
                }
        algo = BaselineOnly(bsl_options=bsl_options)
        trainset = data.build_full_trainset()
        algo.fit(trainset)

        def recipes_to_predict(user_id, df_new):
            # get the list of the recipe ids
            unique_ids = df_new['RecipeId'].unique()

            # get the list of the ids that the userid has watched
            iids1001 = df_new.loc[df_new['UserId']==user_id, 'RecipeId']

            # remove the rated movies for the recommendations
            predict_recipes = np.setdiff1d(unique_ids,iids1001)
            
            return predict_recipes

        def get_recommendations(user_id, df_new, my_recs, thres = 4.8):
            recipes = recipes_to_predict(user_id, df_new)
            
            for iid in recipes:
                estimation = algo.predict(uid=user_id ,iid=iid).est
                print(estimation)
                if estimation >= thres :
                    my_recs.append(iid)
    
            return my_recs

        cos_sim_res = get_recommendations(request.user.id, df_new, cos_sim_res)

        if(len(cos_sim_res)<20):
            cos_sim_res = random.sample(cos_sim_res, len(cos_sim_res))
        else:
            cos_sim_res = random.sample(cos_sim_res, 20)
    else:
        if(len(cos_sim_res)<20):
            cos_sim_res = random.sample(cos_sim_res, len(cos_sim_res))
        else:
            cos_sim_res = random.sample(cos_sim_res, 20)

    if(len(cos_sim_res) == 0):
        recommendations = top_recipes(request)
        return render(request, 'recipes.html', {'recommendations': recommendations, 'name': recipe_name, 'message': True})

    recommendations_df = recipes[recipes['RecipeId'].isin(cos_sim_res)]

    recommendations_df.Images = recommendations_df.Images.str[2:-2]
    recommendations_df.Images = recommendations_df.Images.str.split("'").str[0]

    json_records = recommendations_df.reset_index().to_json(orient ='records')
    data = []
    recommendations = json.loads(json_records)

    return render(request, 'recipes.html', {'recommendations': recommendations, 'name': recipe_name, 'message': True})


    
