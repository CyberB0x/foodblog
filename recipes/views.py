from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from core.forms import ProfileForm
from recipes.models import Profile

from .models import (
    Recipe,
    Category,
    Comment,
    SavedRecipe,
    FavoriteRecipe
)

from .forms import RegisterForm


# HOME PAGE
def home(request):
    query = request.GET.get("q")
    category_slug = request.GET.get("category")

    recipes = Recipe.objects.all().order_by("-created_at")

    # CATEGORY FILTER
    if category_slug:
        recipes = recipes.filter(category__slug=category_slug)

    # SEARCH FILTER
    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(ingredients__icontains=query)
        ).distinct()

    # PAGINATION
    paginator = Paginator(recipes, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # SAVED + FAVORITES IDS
    saved_recipes = []
    favorite_recipes_ids = []

    if request.user.is_authenticated:

        saved_recipes = SavedRecipe.objects.filter(
            user=request.user
        ).values_list("recipe_id", flat=True)

        favorite_recipes_ids = FavoriteRecipe.objects.filter(
            user=request.user
        ).values_list("recipe_id", flat=True)

    return render(request, "home.html", {
        "page_obj": page_obj,
        "query": query,
        "selected_category": category_slug,

        "categories": Category.objects.all(),

        "saved_recipes": saved_recipes,
        "favorite_recipes_ids": favorite_recipes_ids,
    })


# REGISTER
def register_view(request):

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            # AUTO LOGIN
            login(request, user)

            return redirect("/")

    else:
        form = RegisterForm()

    return render(request, "auth/register.html", {
        "form": form
    })


# LOGIN
def login_view(request):

    form = AuthenticationForm(
        request,
        data=request.POST or None
    )

    if request.method == "POST":

        if form.is_valid():
            user = form.get_user()

            login(request, user)

            return redirect("dashboard")

    return render(request, "auth/login.html", {
        "form": form
    })


# LOGOUT
def logout_view(request):
    logout(request)

    return redirect("/")


# PROFILE
@login_required
def profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    context = {
        "profile": profile
    }

    return render(
        request,
        "profile.html",
        context
    )


# DASHBOARD
@login_required
def dashboard(request):

    # SAVED RECIPES
    saved = (
        SavedRecipe.objects
        .filter(user=request.user)
        .select_related("recipe", "recipe__category")
        .order_by("-created_at")
    )

    # FAVORITES
    favorites = (
        FavoriteRecipe.objects
        .filter(user=request.user)
        .select_related("recipe", "recipe__category")
        .order_by("-created_at")
    )

    # PAGINATION
    paginator = Paginator(saved, 6)

    page = request.GET.get("page")

    saved_recipes = paginator.get_page(page)

    categories = Category.objects.all()

    return render(request, "dashboard.html", {

        "saved_recipes": saved_recipes,
        "favorite_recipes": favorites,
        "categories": categories,

        "total_saved": saved.count(),
        "favorite_count": favorites.count(),
    })


# SAVE BUTTON
@login_required
def save_recipe(request, recipe_id):

    if request.method != "POST":
        return redirect("/")

    recipe = get_object_or_404(Recipe, id=recipe_id)

    obj = SavedRecipe.objects.filter(
        user=request.user,
        recipe=recipe
    )

    if obj.exists():
        obj.delete()
    else:
        SavedRecipe.objects.create(
            user=request.user,
            recipe=recipe
        )

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def settings_view(request):

    profile, created = Profile.objects.get_or_create(
        user = request.user
    )

    if request.method == 'POST':

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()

            return redirect('settings')

    else:
        form = ProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
    }

    return render(
        request,
        "settings.html",
        context
    )

# FAVORITE TOGGLE
@login_required
def toggle_favorite(request, id):

    recipe = get_object_or_404(Recipe, id=id)

    obj = FavoriteRecipe.objects.filter(
        user=request.user,
        recipe=recipe
    )

    if obj.exists():
        obj.delete()
        status = "removed"
    else:
        FavoriteRecipe.objects.create(
            user=request.user,
            recipe=recipe
        )
        status = "added"

    return JsonResponse({"status": status})


# RECIPES PAGE
def recipes(request):

    category = request.GET.get("category")

    recipes_list = Recipe.objects.all().order_by("-created_at")

    # FILTER
    if category and category != "all":

        recipes_list = recipes_list.filter(
            category__slug=category
        )

    # PAGINATION
    paginator = Paginator(recipes_list, 6)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    # SAVED + FAVORITES IDS
    saved_recipes = []
    favorite_recipes_ids = []

    if request.user.is_authenticated:

        saved_recipes = SavedRecipe.objects.filter(
            user=request.user
        ).values_list("recipe_id", flat=True)

        favorite_recipes_ids = FavoriteRecipe.objects.filter(
            user=request.user
        ).values_list("recipe_id", flat=True)

    return render(request, "recipes.html", {

        "page_obj": page_obj,
        "recipes": page_obj,

        "categories": Category.objects.all(),

        "selected_category": category,

        "saved_recipes": saved_recipes,
        "favorite_recipes_ids": favorite_recipes_ids,
    })


# ABOUT PAGE
def about(request):
    return render(request, "about.html")


# RECIPE DETAIL
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

    comments = recipe.comments.all().order_by("-created_at")

    # SAVED + FAVORITES IDS
    saved_recipes = []
    favorite_recipes_ids = []

    if request.user.is_authenticated:

        saved_recipes = SavedRecipe.objects.filter(
            user=request.user
        ).values_list("recipe_id", flat=True)

        favorite_recipes_ids = FavoriteRecipe.objects.filter(
            user=request.user
        ).values_list("recipe_id", flat=True)

    return render(request, "recipe_detail.html", {
        "recipe": recipe,
        "comments": comments,

        "saved_recipes": saved_recipes,
        "favorite_recipes_ids": favorite_recipes_ids,
    })


# CATEGORY PAGE
def category_view(request, slug):

    category = get_object_or_404(
        Category,
        slug=slug
    )

    recipes = Recipe.objects.filter(
        category=category
    ).order_by("-created_at")

    paginator = Paginator(recipes, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "home.html", {
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "selected_category": slug,
        "category": category,
    })


# LIVE SEARCH
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

                "image": (
                    r.image.url
                    if r.image
                    else "/static/img/no-image.png"
                )
            })

    return JsonResponse({
        "results": data
    })


# LIKE RECIPE
@login_required
@csrf_exempt
def like_recipe(request, id):

    if request.method == "POST":

        recipe = get_object_or_404(
            Recipe,
            id=id
        )

        liked = request.session.get(
            "liked_recipes",
            []
        )

        liked = [int(x) for x in liked]

        # LIKE
        if id not in liked:

            recipe.likes += 1

            recipe.save()

            liked.append(id)

            request.session["liked_recipes"] = liked

            request.session.modified = True

        return JsonResponse({
            "likes": recipe.likes,
            "liked": True
        })

    return JsonResponse({
        "error": "Invalid request"
    }, status=400)