from django.db import models
from django.contrib.auth.models import User
from sqlalchemy import false
from .validators import validate_avatar
from django.db.models import Avg
from urllib.parse import urlparse, parse_qs


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.TextField()
    instructions = models.TextField()
    image = models.ImageField(upload_to='recipes/images/')
    video_url = models.URLField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    likes = models.PositiveSmallIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)

    prep_time = models.PositiveIntegerField(
        "Preparation time (minutes)",
        default=15
    )

    cook_time = models.PositiveIntegerField(
        "Cooking time (minutes)",
        default=30
    )

    servings = models.PositiveSmallIntegerField(
        default=4
    )

    difficulty = models.CharField(
        max_length=20,
        choices=[
            ("Easy", "Easy"),
            ("Medium", "Medium"),
            ("Hard", "Hard"),
        ],
        default="Easy",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def average_rating(self):
        avg = self.ratings.aggregate(avg=Avg("stars"))["avg"]
        return round(avg or 0, 1)

    @property
    def rating_count(self):
        return self.ratings.count()

    @property
    def ingredients_list(self):
        return [line.strip() for line in self.ingredients.splitlines() if line.strip()]

    @property
    def instructions_list(self):
        return [line.strip() for line in self.instructions.splitlines() if line.strip()]

    def __str__(self):
        return self.title

    def get_youtube_embed_url(self):
        if not self.video_url:
            return None

        url = self.video_url.strip()

        # Уже embed
        if "/embed/" in url:
            return url

        # Обычная ссылка
        if "youtube.com/watch" in url:
            parsed = urlparse(url)
            video_id = parse_qs(parsed.query).get("v", [None])[0]
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"

        # Короткая ссылка
        if "youtu.be/" in url:
            video_id = url.split("youtu.be/")[-1].split("?")[0]
            return f"https://www.youtube.com/embed/{video_id}"

        # Shorts
        if "/shorts/" in url:
            video_id = url.split("/shorts/")[-1].split("?")[0]
            return f"https://www.youtube.com/embed/{video_id}"

        return None

# User profile
class Profile(models.Model):

    CUISINES = [
        ("Italian", "Italian"),
        ("Asian", "Asian"),
        ("Turkish", "Turkish"),
        ("Mexican", "Mexican"),
        ("American", "American"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    avatar = models.ImageField(
        upload_to="avatars/",
        validators=[validate_avatar],
        blank=True,
        null=True
    )

    bio = models.TextField(blank=True)

    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)

    favorite_cuisine = models.CharField(
        max_length=50,
        choices=CUISINES,
        blank=True
    )

    dark_mode = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username
    

# Favorite
class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

# Save Recipe
class SavedRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} saved {self.recipe.title}"


class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=100)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.recipe.title}"



#Rate
class Rating(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ratings"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    stars = models.PositiveSmallIntegerField()

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=("recipe", "user")


    def __str__(self):
        return f"{self.user} - {self.recipe} ({self.stars})"
