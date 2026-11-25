from django.views.generic import ListView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from ..models import Book, Category


class EarlyEdition(ListView):
    """Affiche le listing paginé des livres avec filtre catégorie et recherche mot-clé."""

    model = Book
    template_name = "ReadMe/early-edition.html"
    context_object_name = "books"
    paginate_by = 12

    def _get_selected_category_id(self):
        raw_category = self.request.GET.get("category", "").strip()
        return int(raw_category) if raw_category.isdigit() else None

    def _get_search_query(self):
        return self.request.GET.get("q", "").strip()

    def _is_featured_edition(self):
        # Return True if ?featured_early=1 inside l'URL
        return self.request.GET.get("early_feature", "").strip().lower() in ("1", "true", "on")

    def get_queryset(self):
        queryset = Book.objects.select_related("category").order_by("title")
        selected_category = self._get_selected_category_id()
        search_query = self._get_search_query()
        featured_early = self._is_featured_edition()

        if featured_early:
            queryset = queryset.filter(early_edition=True)

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

        context["categories"] = Category.objects.order_by("name")
        context["selected_category"] = selected_category
        context["search_query"] = search_query
        # Add filter early edition
        context["featured_early"] = self._is_featured_edition()
        # Add number of early_edition book
        context["featured_count"] = Book.objects.filter(early_edition=True).count()
       
        return context

    def post(self, request, *args, **kwargs):
        book_id = request.POST.get("book_id")
        book = get_object_or_404(Book, id=book_id)

        if book.early_edition:
            book.early_edition = False
            book.save()
            messages.success(request, f"« {book.title} » a été retiré de la une.")
        else:
            featured_count = Book.objects.filter(early_edition=True).count()
            if featured_count >= 3:
                messages.error(request, "Vous ne pouvez mettre que trois livres à la une maximum.")
            else:
                book.early_edition = True
                book.save()
                messages.success(request, f"« {book.title} » a été mis à la une.")

        # Redirige vers l'URL exacte avec les paramètres GET actuels (?page=2&category=1...)
        return redirect(request.get_full_path())