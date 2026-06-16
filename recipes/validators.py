from django.core.exceptions import ValidationError

def validate_avatar(image):

    max_size = 5 * 1024 * 1024 # 5MB

    if image.size > max_size:
        raise ValidationError(
            "Image size must be less than 5MB."
        )

    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/webp",
    ]

    if image.content_type not in allowed_types:
        raise ValidationError(
            "Only JPG, PNG and WEBP files are allowed."
        )