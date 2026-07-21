from django.urls import path
from . import views
from .views import dashboard, profile
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Pages
    path("", views.home, name="home"),
    path("recipe/<int:pk>/", views.recipe_detail, name="recipe_detail"),
    path("recipes/", views.recipes, name="recipes"),
    path("about/", views.about, name="about"),

    #Login urls
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", profile, name="profile"),
    path("dashboard/", dashboard, name="dashboard"),


    path("category/<slug:slug>/", views.category_view, name="category"),
    path("like/<int:id>/", views.like_recipe, name="like_recipe"),
    path("favorite/<int:id>/", views.toggle_favorite, name="favorite"),
    path("save/<int:recipe_id>/", views.save_recipe, name="save_recipe"),
    path("live-search/", views.live_search, name="live_search"),
    path('settings/', views.settings_view, name='settings'),
    path("recipe/<int:pk>/rate/", views.rate_recipe, name="rate_recipe"),
    path("recipe/<int:pk>/print/", views.recipe_print, name="recipe_print"),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )