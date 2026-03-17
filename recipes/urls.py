from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("recipe/<int:id>/", views.recipe_detail, name="recipe_detail"),
    path("category/<slug:slug>/", views.category_view, name="category"),
]