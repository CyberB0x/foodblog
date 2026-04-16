from math import trunc
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from sqlalchemy import true

from .models import Recipe, Category, Comment
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.core.paginator import Paginator


def home(request):
    query = request.GET.get("q")
    category_slug = request.GET.get("category")

    recipes = Recipe.objects.all().order_by("-created_at")

    # category filter
    if category_slug:
        recipes = recipes.filter(category__slug=category_slug)

    # search filter
    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(ingredients__icontains=query)
        ).distinct()

    # pagination (ВАЖНО: после фильтров)
    paginator = Paginator(recipes, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "home.html", {
        "page_obj": page_obj,
        "query": query,
        "selected_category": category_slug,
    })


def recipes(request):
    category = request.GET.get("category")
    recipes = Recipe.objects.all().order_by("-created_at")

    # Filter
    if category:
        recipes = recipes.filter(category__slug=category)


    # pagination (ВАЖНО: после фильтров)
    paginator = Paginator(recipes, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "recipes.html", {
        "page_obj": page_obj,
        "recipes": recipes,
        "selected_category": category
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
            return redirect("recipe_detail", id=recipe.id)

    favorites = request.session.get("favorites", [])
    comments = recipe.comments.all().order_by("-created_at")

    return render(request, "recipe_detail.html", {
        "recipe": recipe,
        "comments": comments,
        "favorites": favorites
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


@csrf_exempt
def like_recipe(request, id):
    if request.method == "POST":
        recipe = get_object_or_404(Recipe, id=id)

        liked = request.session.get("liked_recipes", [])

        liked = [int(x) for x in liked]  # FIX 1

        if id not in liked:
            recipe.likes += 1
            recipe.save()

            liked.append(id)
            request.session["liked_recipes"] = liked
            request.session.modified = True  # FIX 2

        return JsonResponse({
            "likes": recipe.likes,
            "liked": True
        })

    return JsonResponse({"error": "Invalid request"}, status=400)


def toggle_favorite(request, id):
    if request.method == "POST":
        favorites = request.session.get("favorites", [])

        if id in favorites:
            favorites.remove(id)
            status = "removed"
        else:
            favorites.append(id)
            status = "added"

        request.session["favorites"] = favorites

        return JsonResponse({"status": status})
