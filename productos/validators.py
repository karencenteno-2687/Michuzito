import os
import re

from django.core.exceptions import ValidationError
from django.conf import settings


def validate_image_file(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    if ext not in valid_extensions:
        raise ValidationError(
            f"Formato de imagen no válido. Permitidos: {', '.join(valid_extensions)}"
        )

    valid_mime_types = ["image/jpeg", "image/png", "image/webp"]
    if hasattr(value, "content_type"):
        if value.content_type not in valid_mime_types:
            raise ValidationError("Tipo MIME de imagen no válido.")

    max_size = getattr(settings, "MAX_IMAGE_SIZE", 5 * 1024 * 1024)
    if value.size > max_size:
        raise ValidationError(
            f"El tamaño máximo permitido es de {max_size // (1024*1024)}MB."
        )


def validate_special_chars(value):
    dangerous_patterns = [
        r"<script.*?>.*?</script>",
        r"on\w+\s*=",
        r"javascript\s*:",
        r"<.*?>",
        r"{{.*?}}",
        r"{%.*?%}",
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, value, re.IGNORECASE | re.DOTALL):
            raise ValidationError(
                "El texto contiene caracteres o scripts no permitidos."
            )
    return value
