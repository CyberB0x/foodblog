from django.db import models


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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_youtube_embed_url(self):
        if not self.video_url:
            return None

        url = self.video_url

        if "youtu.be/" in url:
            video_id = url.split("youtu.be/")[-1]
        elif "watch?v=" in url:
            video_id = url.split("watch?v=")[-1]
        else:
            return None

        video_id = video_id.split("&")[0]
        video_id = video_id.split("?")[0]

        return f"https://www.youtube.com/embed/{video_id}"


class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=100)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.recipe.title}"



