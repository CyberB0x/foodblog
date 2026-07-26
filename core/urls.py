"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from aiohttp.web_fileresponse import content_type
from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.sitemaps.views import sitemap
from recipes.sitemaps import RecipeSitemap
from recipes.image_sitemaps import RecipeImageSitemap
from django.views.generic import TemplateView


sitemaps = {
    "recipes": RecipeSitemap,
}
image_sitemaps = {
    "images": RecipeImageSitemap,
}

handler404 = "recipes.views.custom_404"
handler500 = "recipes.views.custom_500"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path("", include("recipes.urls")),

    path("sitemap.xml", sitemap, {"sitemaps": sitemaps},),
    path("image-sitemap.xml", sitemap, {"sitemaps": image_sitemaps}, name="image-sitemap",),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
