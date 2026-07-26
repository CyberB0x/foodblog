from django.contrib.sitemaps import Sitemap
from .models import Recipe

class RecipeImageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Recipe.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()

    def images(self, obj):
        if obj.image:
            return [{
                "location": obj.image.url,
                "title": obj.title,
                "caption": obj.description,
            }]
        return []