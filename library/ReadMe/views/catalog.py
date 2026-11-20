from django.shortcuts import render

from ..models import Book, Category


def book_catalog(request):
    """Affiche le listing public des livres avec filtre par catégorie."""
    selected_category = request.GET.get("category", "").strip()

    books = Book.objects.select_related("category").order_by("title")
    categories = Category.objects.order_by("name")

    if selected_category.isdigit():
        books = books.filter(category_id=int(selected_category))

    context = {
        "books": books,
        "categories": categories,
        "selected_category": int(selected_category) if selected_category.isdigit() else None,
    }
    return render(request, "ReadMe/catalog.html", context)