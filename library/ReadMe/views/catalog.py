from django.views.generic import ListView

from ..models import Book, Category


class BookCatalogView(ListView):
    """Affiche le listing paginé des livres avec filtre catégorie et recherche auteur."""

    model = Book
    template_name = "ReadMe/catalog.html"
    context_object_name = "books"
    paginate_by = 12

    def _get_selected_category_id(self):
        raw_category = self.request.GET.get("category", "").strip()
        return int(raw_category) if raw_category.isdigit() else None

    def _get_author_query(self):
        return self.request.GET.get("author", "").strip()

    def get_queryset(self):
        queryset = Book.objects.select_related("category").order_by("title")
        selected_category = self._get_selected_category_id()
        author_query = self._get_author_query()

        if selected_category is not None:
            queryset = queryset.filter(category_id=selected_category)

        if author_query:
            queryset = queryset.filter(author__icontains=author_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.order_by("name")
        context["selected_category"] = self._get_selected_category_id()
        context["selected_author"] = self._get_author_query()
        return context