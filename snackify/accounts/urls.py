from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/',views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('home', views.home, name='home'),
    path('recipe_names', views.all_recipes, name='recipes_names'),
]