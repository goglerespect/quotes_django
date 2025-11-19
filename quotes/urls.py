from django.urls import path
from . import views

app_name = "quotes"

urlpatterns = [
    path("", views.quote_list, name="quote_list"),
    path("author/<int:pk>/", views.author_detail, name="author_detail"),

    path("add_author/", views.add_author, name="add_author"),
    path("add_quote/", views.add_quote, name="add_quote"),

    path("register/", views.register_view, name="register"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
]