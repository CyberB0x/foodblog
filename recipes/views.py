from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Recipe, Category


def home(request):
    query = request.GET.get("q")

    recipes = Recipe.objects.all().order_by("-created_at")

    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) |
            Q(description__icontrains=query) |
            Q(ingredients__icontains=query)
        ).distinct()

    return render(request, "home.html", {
        "recipes": recipes,
        "query": query
    })

def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    return render(request, "recipe_detail.html", {"recipe": recipe})


def category_view(request, slug):

    category = get_object_or_404(Category, slug=slug)
    recipes = Recipe.objects.filter(category=category)

    return render(request, "home.html", {
        "recipies": recipes,
        "category": category
    })