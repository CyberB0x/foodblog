from django.shortcuts import render, get_object_or_404
from .models import Recipe


def home(request):
    recipes = Recipe.objects.all().order_by("-created_at")
    return render(request, "home.html", {"recipes": recipes})

def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    return render(request, "recipe_detail.html", {"recipe": recipe})
