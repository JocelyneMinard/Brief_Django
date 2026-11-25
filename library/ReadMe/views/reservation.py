from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

from ..models import (
    ACTIVE_RESERVATION_STATUSES,
    MAX_ACTIVE_RESERVATIONS_PER_USER,
    Book,
    Reservation,
)
from .cross_sell import CrossSellMixin


class ReservationView(CrossSellMixin, ListView):
    """
    Display a user's reservations filtered by status group along with cross-sell data
    """

    model: type[Reservation] = Reservation
    template_name: str = "ReadMe/reservation.html"
    context_object_name: str = "reservations"

    # Map high-level UI tabs to underlying reservation status codes.
    status_group: dict[str, list[str]] = {
        "active": ["prete", "empruntee"],
        "pending": ["en_attente"],
        "archived": ["rendue", "annulee"],
    }

    def get_queryset(self) -> QuerySet[Reservation]:
        """
        Return reservations for the target user, optionally filtered by the active tab
        """
        user_id: int | None = self.kwargs.get("pk")
        active_tab: str = self.request.GET.get("tab", "all")

        # Preload book to avoid other queries when rendering titles in the template.
        queryset: QuerySet[Reservation] = (
            Reservation.objects.filter(user_id=user_id)
            .select_related("book")
            .order_by("-creation_date")
        )
        if active_tab in self.status_group:
            queryset = queryset.filter(status__in=self.status_group[active_tab])

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Include the active tab name in context for active tab styling
        """
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["active_tab"] = self.request.GET.get("tab", "all")
        return context


class BookReserveView(LoginRequiredMixin, View):
    """
    Handle book reservation requests for authenticated users via AJAX or standard POST
    """

    @staticmethod
    def _wants_json(request: HttpRequest) -> bool:
        """Detect whether the client expects a JSON response rather than a redirect."""
        return (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            or "application/json" in request.headers.get("Accept", "")
        )

    @staticmethod
    def _get_available_quantity(book: Book) -> int:
        """
        Compute remaining reservable copies for a book based on active reservations
        """
        active_count: int = Reservation.objects.filter(
            book=book,
            status__in=ACTIVE_RESERVATION_STATUSES,
        ).count()
        return max(0, book.quantity - active_count)

    def _respond(
        self,
        request: HttpRequest,
        book: Book,
        level: str,
        text: str,
        status_code: int,
        available_quantity: int | None = None,
        redirect_url_name: str = "ReadMe:book_details",
    ) -> HttpResponse:
        """
        Return a JSON payload for AJAX requests or a flashed redirect for normal forms
        """
        if available_quantity is None:
            available_quantity = self._get_available_quantity(book)

        if self._wants_json(request):
            return JsonResponse(
                {
                    "ok": level == "success",
                    "level": level,
                    "message": text,
                    "available_quantity": available_quantity,
                },
                status=status_code,
            )

        # Dynamically dispatch to messages.success, messages.warning, or messages.error
        getattr(messages, level)(request, text)
        return redirect(redirect_url_name, pk=book.pk)

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """
        Validate business rules and create a reservation inside an atomic transaction
        """
        today = timezone.localdate()
        outcome: tuple[str, str, int, int] | None = None

        with transaction.atomic():
            # Lock the target book row when supported so concurrent reservations serialize cleanly
            book: Book = get_object_or_404(Book.objects.select_for_update(), pk=pk)

            active_count: int = Reservation.objects.filter(
                book=book,
                status__in=ACTIVE_RESERVATION_STATUSES,
            ).count()
            available_before: int = max(0, book.quantity - active_count)

            # Check 1: ensure at least one copy of the book is still available
            if active_count >= book.quantity:
                outcome = (
                    "error",
                    "Réservation impossible : tous les exemplaires actifs sont déjà réservés ou empruntés.",
                    409,
                    0,
                )
            else:
                user_active_count: int = Reservation.objects.filter(
                    user=request.user,
                    status__in=ACTIVE_RESERVATION_STATUSES,
                ).count()

                # Check 2: enforce the per-user active reservation cap.
                if user_active_count >= MAX_ACTIVE_RESERVATIONS_PER_USER:
                    outcome = (
                        "error",
                        f"Réservation impossible : vous avez déjà {MAX_ACTIVE_RESERVATIONS_PER_USER} réservations actives (maximum autorisé).",
                        409,
                        available_before,
                    )
                # Check 3: prevent duplicate active reservations on the same book by the same user
                elif Reservation.objects.filter(
                    book=book,
                    user=request.user,
                    status__in=ACTIVE_RESERVATION_STATUSES,
                ).exists():
                    outcome = (
                        "warning",
                        "Réservation impossible : vous avez déjà une réservation active sur ce livre.",
                        409,
                        available_before,
                    )
                else:
                    reservation = Reservation(
                        user=request.user,
                        book=book,
                        status="en_attente",
                        creation_date=today,
                        last_update=today,
                    )
                    try:
                        # Run model-level validation before saving to catch constraint/rule violations early
                        reservation.full_clean()
                        reservation.save()
                    except ValidationError as exc:
                        reason = "; ".join(
                            msg
                            for msgs in (
                                exc.message_dict.values()
                                if hasattr(exc, "message_dict")
                                else [exc.messages]
                            )
                            for msg in msgs
                        ) or "La validation de la réservation a échoué."
                        outcome = (
                            "error",
                            f"Réservation impossible : {reason}",
                            400,
                            available_before,
                        )
                    except IntegrityError as exc:
                        outcome = (
                            "error",
                            f"Réservation impossible : contrainte base de données non respectée ({exc}).",
                            400,
                            available_before,
                        )
                    else:
                        outcome = (
                            "success",
                            f"Réservation confirmée pour « {book.title} » (statut : en attente).",
                            201,
                            max(0, available_before - 1),
                        )

        # Exit the atomic block before building the response so any post-response queries run outside the transaction
        assert outcome is not None
        level, text, status_code, avail_qty = outcome
        return self._respond(
            request,
            book,
            level=level,
            text=text,
            status_code=status_code,
            available_quantity=avail_qty,
        )