from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from .models import recipes_info

def home(request):
    return render(request, 'home.html')

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
    return render(request, 'recipes_names.html', 
    {'Name': Name})