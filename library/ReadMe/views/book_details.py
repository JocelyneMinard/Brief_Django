import hashlib
from django.templatetags.static import static
from django.views.generic import DetailView

from ..models import Book
from .catalog import COVER_FILES, is_valid_cover_path
from .cross_sell import CrossSellMixin



class BookDetailView(CrossSellMixin, DetailView):
    """Affiche la fiche détaillée d'un livre."""

    model = Book
    template_name = "ReadMe/book_details.html"
    context_object_name = "book"

    def get_queryset(self):
        return Book.objects.select_related("category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        requested_cover = self.request.GET.get("cover")

        if is_valid_cover_path(requested_cover):
            chosen_cover = requested_cover
        else:
            digest = int(hashlib.md5(f"book:{self.object.pk}".encode()).hexdigest(), 16)
            chosen_cover = COVER_FILES[digest % len(COVER_FILES)]

        context["cover_path"] = chosen_cover
        context["cover_url"] = static(chosen_cover)
        return context