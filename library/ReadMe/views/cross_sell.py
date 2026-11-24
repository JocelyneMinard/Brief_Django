import hashlib
from django.templatetags.static import static

from ..models import Book
from .catalog import COVER_FILES


class CrossSellMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_books"] = (
            Book.objects.filter(early_edition=True)
            .select_related("category")[:3]
        )
        for book in context["featured_books"]:
            digest = int(hashlib.md5(f"book:{book.pk}".encode()).hexdigest(), 16)
            chosen_cover = COVER_FILES[digest % len(COVER_FILES)]
            book.cover_path = chosen_cover
            book.cover_url = static(chosen_cover)

        return context
    