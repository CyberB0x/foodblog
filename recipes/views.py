from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, F
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
from django.db.models import Avg
from django.db.models import F

from core.forms import ProfileForm
from recipes.models import Profile

from .models import (
    Recipe,
    Category,
    Comment,
    SavedRecipe,
    FavoriteRecipe,
    Rating
)



# =========================
# HOME PAGE
# =========================
def home(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category")

    recipes = Recipe.objects.all().order_by("-created_at")

    # CATEGORY FILTER
    if category_slug:
        recipes = recipes.filter(category__slug=category_slug)

    # SEARCH FILTER
    if query:
        query = query[:100]
        recipes = recipes.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(ingredients__icontains=query)
        ).distinct()

    # PAGINATION
    paginator = Paginator(recipes, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

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



# =========================
# LOGIN
# =========================
def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")

    return render(request, "auth/login.html", {
        "form": form
    })


# =========================
# LOGOUT
# =========================
def logout_view(request):
    logout(request)
    return redirect("/")


# =========================
# PROFILE
# =========================
@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    return render(request, "profile.html", {
        "profile": profile
    })


# =========================
# DASHBOARD
# =========================
@login_required
def dashboard(request):

    saved = (
        SavedRecipe.objects
        .filter(user=request.user)
        .select_related("recipe", "recipe__category")
        .order_by("-created_at")
    )

    favorites = (
        FavoriteRecipe.objects
        .filter(user=request.user)
        .select_related("recipe", "recipe__category")
        .order_by("-created_at")
    )

    paginator = Paginator(saved, 6)
    page = request.GET.get("page")
    saved_recipes = paginator.get_page(page)

    return render(request, "dashboard.html", {
        "saved_recipes": saved_recipes,
        "favorite_recipes": favorites,
        "categories": Category.objects.all(),
        "total_saved": saved.count(),
        "favorite_count": favorites.count(),
    })


# =========================
# SAVE / UNSAVE
# =========================
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

    return redirect(request.META.get("HTTP_REFERER", "/"))


# =========================
# SETTINGS
# =========================
@login_required
def settings_view(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()
            return redirect("settings")

    else:
        form = ProfileForm(instance=profile)

    return render(request, "settings.html", {
        "form": form,
        "profile": profile,
    })


# =========================
# FAVORITE TOGGLE
# =========================
@login_required
def toggle_favorite(request, id):

    if request.method != "POST":
        return redirect("dashboard")

    recipe = get_object_or_404(Recipe, id=id)

    favorite = FavoriteRecipe.objects.filter(
        user=request.user,
        recipe=recipe
    )

    if favorite.exists():
        favorite.delete()
    else:
        FavoriteRecipe.objects.filter(
            user=request.user,
            recipe=recipe
        )

    next_page = request.POST.get("next")

    if next_page:
        return redirect(next_page)

    return redirect("recipe_detail", id=id)




# =========================
# RECIPES PAGE
# =========================
def recipes(request):

    category = request.GET.get("category")

    recipes_list = Recipe.objects.all().order_by("-created_at")

    if category and category != "all":
        recipes_list = recipes_list.filter(category__slug=category)

    paginator = Paginator(recipes_list, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

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


# =========================
# ABOUT
# =========================
def about(request):
    return render(request, "about.html")


# =========================
# RECIPE DETAIL + COMMENTS
# =========================
@ratelimit(key='ip', rate='5/m')
def recipe_detail(request, pk):

    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == "POST":

        name = (request.POST.get("name") or "").strip()
        text = (request.POST.get("text") or "").strip()

        if name and text:

            if len(text) > 1000:
                return redirect("recipe_detail", id=recipe.id)

            Comment.objects.create(
                recipe=recipe,
                name=name,
                text=text
            )

            return redirect("recipe_detail", pk=recipe.id)

    comments = recipe.comments.all().order_by("-created_at")

    saved_recipes = []
    favorite_recipes_ids = []

    if request.user.is_authenticated:
        saved_recipes = SavedRecipe.objects.filter(
            user=request.user
        ).values_list("recipe_id", flat=True)

        favorite_recipes_ids = FavoriteRecipe.objects.filter(
            user=request.user
        ).values_list("recipe_id", flat=True)

    recipe.views = F("views") + 1
    recipe.save(update_fields=["views"])
    recipe.refresh_from_db()

    # Similar_recipes
    similar_recipes = (
        Recipe.objects.filter(category=recipe.category)
        .exclude(id=recipe.id)
        .order_by("?")[:3]
    )

    return render(request, "recipe_detail.html", {
        "recipe": recipe,
        "comments": comments,
        "saved_recipes": saved_recipes,
        "favorite_recipes_ids": favorite_recipes_ids,
        "similar_recipes": similar_recipes,

        #SEO Open Graph
        "meta_title": f"{recipe.title} | Food Blog",
        "meta_description": recipe.description[:160],
        "meta_image": (
            request.build_absolute_uri(recipe.image.url)
            if recipe.image
            else ""
        ),
    })


# =========================
# CATEGORY PAGE
# =========================
def category_view(request, slug):

    category = get_object_or_404(Category, slug=slug)

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


# =========================
# LIVE SEARCH
# =========================
@ratelimit(key='ip', rate='30/m')
def live_search(request):

    query = (request.GET.get("q") or "").strip()
    data = []

    if query:
        query = query[:100]

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

    return JsonResponse({"results": data})


# =========================
# LIKE RECIPE (SAFE + ATOMIC)
# =========================
@login_required
@ratelimit(key='user', rate='20/m')
def like_recipe(request, id):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    recipe = get_object_or_404(Recipe, id=id)

    liked = request.session.get("liked_recipes", [])
    liked = [int(x) for x in liked]

    if id not in liked:

        Recipe.objects.filter(id=id).update(
            likes=F("likes") + 1
        )

        liked.append(id)
        request.session["liked_recipes"] = liked
        request.session.modified = True

    recipe.refresh_from_db()

    return JsonResponse({
        "likes": recipe.likes,
        "liked": True
    })

# Rating
@login_required
def rate_recipe(request, pk):
    if request.method != "POST":
        return JsonResponse({"success": False}, status=400)

    recipe = get_object_or_404(Recipe, pk=pk)

    try:
        stars = int(request.POST.get("stars"))
    except (TypeError, ValueError):
        return JsonResponse(
            {"success": False, "message": "Invalid rating"},
            status=400
        )

    if stars < 1 or stars > 5:
        return JsonResponse(
            {"success": False, "message": "Rating must be between 1 and 5"},
            status=400
        )

    rating, created = Rating.objects.update_or_create(
        recipe=recipe,
        user=request.user,
        defaults={"stars": stars},
    )

    average = recipe.ratings.aggregate(avg=Avg("stars"))["avg"] or 0

    return JsonResponse({
        "success": True,
        "average": round(average, 1),
        "count": recipe.ratings.count(),
        "your_rating": rating.stars,
    })

# Print
def recipe_print(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)

    return render(request, "recipe_print.html",{"recipe":recipe})