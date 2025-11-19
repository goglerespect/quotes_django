from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView

from .forms import RegisterForm, AuthorForm, QuoteForm
from .models import Author, Quote


# Список цитат (публічно)
def quote_list(request):
    quotes = Quote.objects.select_related("author").all()
    return render(request, "quotes/quote_list.html", {"quotes": quotes})


# Сторінка автора (публічно)
def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    return render(request, "quotes/author_detail.html", {"author": author})


# Додавання автора (тільки для логінених)
@login_required
def add_author(request):
    if request.method == "POST":
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("quotes:quote_list")
    else:
        form = AuthorForm()
    return render(request, "quotes/add_author.html", {"form": form})


# Додавання цитати (тільки для логінених)
@login_required
def add_quote(request):
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("quotes:quote_list")
    else:
        form = QuoteForm()
    return render(request, "quotes/add_quote.html", {"form": form})


# Реєстрація
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("quotes:quote_list")
    else:
        form = RegisterForm()
    return render(request, "quotes/register.html", {"form": form})


# Логін / Логаут
class CustomLoginView(LoginView):
    template_name = "quotes/login.html"


class CustomLogoutView(LogoutView):
    next_page = "quotes:quote_list"
