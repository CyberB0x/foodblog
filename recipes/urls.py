from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("recipe/<int:id>/", views.recipe_detail, name="recipe_detail"),
    path("category/<slug:slug>/", views.category_view, name="category"),
    path("like/<int:id>/", views.like_recipe, name="like_recipe"),
    path("live-search/", views.live_search, name="live_search"),
]