from django.views.generic import ListView
from django.templatetags.static import static
import random
from django.db.models import Q

from ..models import Book, Category

COVER_FILES = [f"ReadMe/img/covers/cover-{i:02d}.jpg" for i in range(1, 13)]


def is_valid_cover_path(cover_path: str | None) -> bool:
    """Vérifie que le chemin demandé fait bien partie de la liste autorisée."""
    return bool(cover_path and cover_path in COVER_FILES)


def assign_page_covers(books_page, page_seed: str = "page-1"):
    """Assigne une couverture distincte parmi les 12 à chaque livre de la page."""
    pool = COVER_FILES.copy()
    rng = random.Random(page_seed)
    rng.shuffle(pool)

    for idx, book in enumerate(books_page):
        cover_path = pool[idx % len(pool)]
        book.cover_path = cover_path
        book.cover_url = static(cover_path)


class BookCatalogView(ListView):
    """Affiche le listing paginé des livres avec filtre catégorie et recherche mot-clé."""

    model = Book
    template_name = "ReadMe/catalog.html"
    context_object_name = "books"
    paginate_by = 12

    def _get_selected_category_id(self):
        raw_category = self.request.GET.get("category", "").strip()
        return int(raw_category) if raw_category.isdigit() else None

    def _get_search_query(self):
        return self.request.GET.get("q", "").strip()

    def get_queryset(self):
        queryset = Book.objects.select_related("category").order_by("title")
        selected_category = self._get_selected_category_id()
        search_query = self._get_search_query()

        if selected_category is not None:
            queryset = queryset.filter(category_id=selected_category)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(author__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_category = self._get_selected_category_id()
        search_query = self._get_search_query()

        page_obj = context.get("page_obj")
        page_number = page_obj.number if page_obj else 1
        page_seed = f"page-{page_number}-cat-{selected_category or 'all'}-q-{search_query.lower()}"

        assign_page_covers(context["books"], page_seed=page_seed)

        context["categories"] = Category.objects.order_by("name")
        context["selected_category"] = selected_category
        context["search_query"] = search_query
        return context