from math import trunc
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from sqlalchemy import true

from .models import Recipe, Category, Comment, SavedRecipe
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required


# home page
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


# Register and Login form
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # auto login
            return redirect("/")
    else:
        form = RegisterForm()
    return render(request, "auth/register.html", {"form": form})

def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("/")

    return render(request, "auth/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("/")


# User Dashboard
@login_required
def dashboard(request):
    category = request.GET.get("category")

    saved = (
        SavedRecipe.objects
        .filter(user=request.user)
        .select_related("recipe", "recipe__category")
        .order_by("-created_at")
    )

    if category:
        saved = saved.filter(recipe__category__slug=category)

    categories = Category.objects.all()

    paginator = Paginator(saved, 6)
    page = request.GET.get("page")
    saved_recipes = paginator.get_page(page)

    return render(request, "dashboard.html", {
        "saved_recipes": saved_recipes,
        "categories": categories,
        "current_category": category,
        "total_saved": saved.count()  #  для UI
    })

# Save btn
@login_required
def save_recipe(request, id):
    recipe = get_object_or_404(Recipe, id=id)

    obj, created = SavedRecipe.objects.get_or_create(
        user=request.user,
        recipe=recipe
    )

    if not created:
        obj.delete()
        saved = False
    else:
        saved = True
    return JsonResponse({"saved": saved})


# recipe page
def recipes(request):
    category = request.GET.get("category")

    recipes_list = Recipe.objects.all().order_by("-created_at")

    # ФИЛЬТР
    if category and category != "all":
        recipes_list = recipes_list.filter(category__slug=category)

    # PAGINATION (после фильтра!)
    paginator = Paginator(recipes_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "recipes.html", {
        "page_obj": page_obj,
        "recipes": page_obj,  # ВАЖНО
        "categories": Category.objects.all(),  # для меню
        "selected_category": category
    })

# about page
def about(request):
    return render(request, "about.html")


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
                "image": r.image.url if r.image else "/static/img/no-image.png"
            })

    return JsonResponse({"results": data})


@login_required
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


@login_required
def toggle_favorite(request, id):
    if request.method == "POST":
        recipe = get_object_or_404(Recipe, id=id)

        favorites = request.session.get("favorites", [])

        if id in favorites:
            favorites.remove(id)
            status = "removed"
        else:
            favorites.append(id)
            status = "added"

        request.session["favorites"] = favorites
        request.session.modified = True  # ВАЖНО

        return JsonResponse({
            "status": status,
            "favorites_count": len(favorites)
        })