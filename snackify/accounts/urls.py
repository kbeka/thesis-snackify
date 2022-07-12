from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/',views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('home/', views.home, name='home'),
    path('about_us/', views.about_us, name='about_us'),
    path('recipes', views.all_recipes, name='recipes'),
    path('recipe_information/<RecipeId>', views.recipe_page, name='recipe_page'),
    path('profile/<username>', views.profile_info, name='profile_info'),
    path('profile/<username>/edit_profile', views.edit_profile, name='edit_profile'),
    path('profile/<username>/password-change', views.change_password, name='password_change'),
    path('profile/<username>/cookbook', views.cookbook, name='cookbook'),
    path('profile/<username>/favorite', views.favorite, name='favorite'),
    path('recipe_information/<RecipeId>/addFavoriteRecipe', views.add_favorite, name='add_favorite'),
    path('recipe_information/<RecipeId>/addToCookbook', views.add_cookbook, name='add_cookbook'),
    path('recipe_information/<RecipeId>/removeFavoriteRecipe', views.remove_favorite, name='remove_favorite'),
    path('recipe_information/<RecipeId>/removeFromCookbook', views.remove_cookbook, name='remove_cookbook'),
    path('recipe_information/<RecipeId>/rating', views.recipe_page, name='rate'),
    path('recipe_information/<RecipeId>/review', views.recipe_page, name='review'),
    path('recipe_information/<RecipeId>/delete_review', views.delete_review, name='delete_review'),
    path('categories', views.categories_page, name='categories_page'),
    path('categories/<path:category>', views.category_recipes, name='category_recipes'),
    path('ingredients/<ingredients>', views.ingredient_recipes, name='ingredient_recipes'),
    path('ingredients', views.ingredients_page, name='ingredients_page'),
    path('search_results', views.search, name='search'),
    path('nutrition', views.nutrition_page, name='nutrition_page'),
    path('nutrition/search_results', views.nutrition_recipes, name='nutrition_recipes'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)