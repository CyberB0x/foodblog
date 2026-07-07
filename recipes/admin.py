from django.contrib import admin
from .models import Recipe, Category, Comment


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "category",
        "difficulty",
        "prep_time",
        "cook_time",
        "servings",
        "likes",
        "views",
        "created_at",
    )

    list_filter = (
        "category",
        "difficulty",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "ingredients",
    )

    readonly_fields = (
        "likes",
        "views",
        "created_at",
    )

    fieldsets = (
        (
            "Recipe Information",
            {
                "fields": (
                    "title",
                    "category",
                    "image",
                    "video_url",
                )
            },
        ),
        (
            "Cooking Details",
            {
                "fields": (
                    "prep_time",
                    "cook_time",
                    "servings",
                    "difficulty",
                )
            },
        ),
        (
            "Recipe Content",
            {
                "fields": (
                    "description",
                    "ingredients",
                    "instructions",
                )
            },
        ),
        (
            "Statistics",
            {
                "fields": (
                    "likes",
                    "views",
                    "created_at",
                )
            },
        ),
    )


admin.site.register(Category)
admin.site.register(Comment)