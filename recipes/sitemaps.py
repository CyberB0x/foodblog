from django.contrib.sitemaps import Sitemap
from .models import Recipe

class RecipeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Recipe.objects.all()

