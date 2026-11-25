import hashlib
from django.templatetags.static import static
from django.views.generic import DetailView

from ..models import Book
from .catalog import COVER_FILES, is_valid_cover_path
from .cross_sell import CrossSellMixin



class BookDetailView(CrossSellMixin, DetailView):
    """
    Display details for a single book along with its resolved cover and cross-sell data
    """

    # Configure the correct name, template and context to this view
    model = Book
    template_name = "ReadMe/book_details.html"
    context_object_name = "book"

    def get_queryset(self):
        """
        Return the book queryset with category preloaded to avoid extra queries
        """
        return Book.objects.select_related("category")

    def get_context_data(self, **kwargs):
        """
        Add the resolved cover asset path and static URL to the template context
        This function would disapear if a cover column is added in future updates
        """
        context = super().get_context_data(**kwargs)
        requested_cover = self.request.GET.get("cover")

        # Use the query-string cover if valid, otherwise fall back to a deterministic cover per book
        if is_valid_cover_path(requested_cover):
            chosen_cover = requested_cover
        else:
            # instead of random choice which would change the cover every refresh, here we determine the same cover everytime with his pk
            digest = int(hashlib.md5(f"book:{self.object.pk}".encode()).hexdigest(), 16)
            chosen_cover = COVER_FILES[digest % len(COVER_FILES)]

        context["cover_path"] = chosen_cover
        context["cover_url"] = static(chosen_cover)
        return context