from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Author, Quote

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ("fullname", "born_date", "born_location", "description")

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ("quote", "author", "tags")