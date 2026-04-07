from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Recipe, Category, Comment
from django.http import JsonResponse


def home(request):
    query = request.GET.get("q")
    category_slug = request.GET.get("category")

    recipes = Recipe.objects.all().order_by("-created_at")

    if category_slug:
        recipes = recipes.filter(category__slug=category_slug)

    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(ingredients__icontains=query)
        ).distinct()

    return render(request, "home.html", {
        "recipes": recipes,
        "query": query,
        "selected_category": category_slug
    })

def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)

    if request.method == "POST":
        name = request.POST.get("name")
        text = request.POST.get("text")

        if name and text:
            Comment.objects.create(
                recipe=recipe,
                name=name,
                text=text
            )

    comments = recipe.comments.all().order_by("-created_at")

    return render(request, "recipe_detail.html",{
        "recipe": recipe,
        "comments": comments
    })


def category_view(request, slug):

    category = get_object_or_404(Category, slug=slug)
    recipes = Recipe.objects.filter(category=category)

    return render(request, "home.html", {
        "recipes": recipes,
        "category": category
    })


def live_search(request):
    query = request.GET.get("q")

    data = []

    if query:
        results = Recipe.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )[:5]

        for r in results:
            data.append({
                "id": r.id,
                "title": r.title,
                "image": r.image.url
            })

    return JsonResponse({"results": data})