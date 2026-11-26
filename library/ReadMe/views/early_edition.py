from django.views.generic import ListView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from ..models import Book, Category


class EarlyEdition(ListView):
    """
    Display a paginated list of books with category filtering, keyword search,
    early-edition filtering, and toggling of featured early-edition status.
    """

    model = Book
    template_name = "ReadMe/early-edition.html"
    context_object_name = "books"
    paginate_by = 12

    def _get_selected_category_id(self):
        """
        Extract and validate the selected category ID from the query parameters.

        Returns:
            int | None: The category primary key if valid, otherwise None.
        """
        raw_category = self.request.GET.get("category", "").strip()
        return int(raw_category) if raw_category.isdigit() else None

    def _get_search_query(self):
        """
        Retrieve the trimmed search keyword from the query parameters.

        Returns:
            str: The search query string, or an empty string if absent.
        """
        return self.request.GET.get("q", "").strip()

    def _is_featured_edition(self):
        """
        Check whether the early-edition filter is enabled in the query parameters.

        Returns:
            bool: True if `early_feature` is set to '1', 'true', or 'on';
                otherwise False.
        """
        return self.request.GET.get("early_feature", "").strip().lower() in ("1", "true", "on")

    def get_queryset(self):
        """
        Build the filtered and alphabetically ordered queryset of books based on
        early-edition status, category ID, and title/author search query.

        Returns:
            QuerySet: Filtered `Book` queryset ordered by title.
        """
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
        """
        Populate the template context with categories, active filters, and the
        total count of featured early-edition books.

        Args:
            **kwargs: Arbitrary keyword arguments passed to the parent
                `get_context_data` method.

        Returns:
            dict: The updated template context.
        """
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
        """
        Toggle the `early_edition` featured status of a book, enforcing a maximum
        limit of three featured books at a time.

        Args:
            request (HttpRequest): The incoming POST HTTP request containing `book_id`.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponseRedirect: Redirects back to the current full URL,
                preserving active GET parameters.
        """
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