from collections.abc import Iterable
import random
from typing import Any

from django.db.models import Q, QuerySet
from django.templatetags.static import static
from django.views.generic import ListView

from ..models import Book, Category

COVER_FILES: list[str] = [f"ReadMe/img/covers/cover-{i:02d}.jpg" for i in range(1, 13)]


def is_valid_cover_path(cover_path: str | None) -> bool:
    """
    Return whether the requested cover path belongs to the allowed cover list
    This will disappear if the cover column is added
    """
    return bool(cover_path and cover_path in COVER_FILES)


def assign_page_covers(books_page: Iterable[Book], page_seed: str = "page-1") -> None:
    """
    Assign a deterministically shuffled cover path and static URL to each book on the page
    This will disappeear if the cover column is added
    """
    # Shuffle a copy per page seed so covers stay consistent for a given view state without mutating COVER_FILES.
    pool: list[str] = COVER_FILES.copy()
    rng = random.Random(page_seed)
    rng.shuffle(pool)

    for idx, book in enumerate(books_page):
        cover_path: str = pool[idx % len(pool)]
        book.cover_path = cover_path
        book.cover_url = static(cover_path)


class BookCatalogView(ListView):
    """
    Display a paginated book catalog with category filtering and keyword search
    """

    model: type[Book] = Book
    template_name: str = "ReadMe/catalog.html"
    context_object_name: str = "books"
    paginate_by: int = 12

    def _get_selected_category_id(self) -> int | None:
        """
        Parse and return the numeric category ID from query parameters, if present
        """
        raw_category: str = self.request.GET.get("category", "").strip()
        return int(raw_category) if raw_category.isdigit() else None

    def _get_search_query(self) -> str:
        """
        Return the trimmed search query string from GET parameters
        """
        return self.request.GET.get("q", "").strip()

    def get_queryset(self) -> QuerySet[Book]:
        """
        Return ordered books filtered by optional category ID and search keyword
        """
        queryset: QuerySet[Book] = Book.objects.select_related("category").order_by("title")
        selected_category: int | None = self._get_selected_category_id()
        search_query: str = self._get_search_query()

        if selected_category is not None:
            queryset = queryset.filter(category_id=selected_category)

        if search_query:
            # Match against either title or author case-insensitively
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(author__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Populate template context with page covers, categories, and active filter state
        The cover part will disappear if the cover column is added
        """
        context: dict[str, Any] = super().get_context_data(**kwargs)
        selected_category: int | None = self._get_selected_category_id()
        search_query: str = self._get_search_query()

        page_obj = context.get("page_obj")
        page_number: int = page_obj.number if page_obj else 1

        # Include page, category, and query in the seed so each filter/page state resolves deterministically.
        page_seed: str = f"page-{page_number}-cat-{selected_category or 'all'}-q-{search_query.lower()}"
        assign_page_covers(context["books"], page_seed=page_seed)

        context["categories"] = Category.objects.order_by("name")
        context["selected_category"] = selected_category
        context["search_query"] = search_query
        return context