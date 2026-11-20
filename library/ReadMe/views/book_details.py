from django.views.generic import DetailView

from ..models import Book


class BookDetailView(DetailView):
    """Affiche la fiche détaillée d'un livre."""

    model = Book
    template_name = "ReadMe/book_details.html"
    context_object_name = "book"

    def get_queryset(self):
        return Book.objects.select_related("category")