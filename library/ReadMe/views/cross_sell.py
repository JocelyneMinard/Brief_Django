import hashlib
from django.templatetags.static import static

from ..models import Book
from .catalog import COVER_FILES


class CrossSellMixin:
    """
    Mixin adding featured early-edition books with deterministic cover images
    to the template context.
    """
    def get_context_data(self, **kwargs):
        """
        Populate the template context with up to three early-edition books and
        assign each a deterministic static cover image based on its primary key.

        Args:
            **kwargs: Arbitrary keyword arguments passed to the parent
                `get_context_data` method.

        Returns:
            dict: The updated template context containing `featured_books`.
        """
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
    