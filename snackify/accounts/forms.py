from django import forms
from .models import interactions, RATE_CHOICES, profile
from django.contrib.auth.models import User
from django.forms.widgets import DateInput
from datetime import datetime,date


class RatingForm(forms.ModelForm):
    rating = forms.ChoiceField(choices=RATE_CHOICES, required=True)

    class Meta:
        model = interactions
        fields = ['rating']

class ReviewForm(forms.ModelForm):
    review = forms.CharField(widget=forms.Textarea(attrs={"rows":3, 'class': 'form-control', 'id': 'exampleFormControlTextarea1', 'placeholder': 'Write your review...'}))

    class Meta:
        model = interactions
        fields = ['review']

class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
                               widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    email = forms.EmailField(
                             widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    first_name = forms.CharField(max_length=100,
                               widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    last_name = forms.CharField(max_length=100,
                               widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
                             
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class UpdateProfileForm(forms.ModelForm):
    birthday = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}), required=False)
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control', 'type': 'file', 'id': 'formFile'}), required=False)
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
     
    class Meta:
        model = profile
        fields = ['birthday', 'image', 'city']
