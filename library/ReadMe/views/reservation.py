from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from django.core.exceptions import ValidationError
from django.http import JsonResponse

from ..models import (
    ACTIVE_RESERVATION_STATUSES,
    MAX_ACTIVE_RESERVATIONS_PER_USER,
    Book,
    Reservation,
)



class ReservationView(ListView):
    model = Reservation
    template_name = "ReadMe/reservation.html"
    context_object_name = "reservations"

    def get_queryset(self):
        user_id = self.kwargs.get("pk")
        # write on multiple line for resct Python onvention
        # select_related on book for have title
        return (
            Reservation.objects.filter(user_id = user_id)
            .select_related("book")
            .order_by("-creation_date")
        )


class BookReserveView(LoginRequiredMixin, View):
    @staticmethod
    def _wants_json(request):
        return (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            or "application/json" in request.headers.get("Accept", "")
        )

    @staticmethod
    def _get_available_quantity(book):
        active_count = Reservation.objects.filter(
            book=book,
            status__in=ACTIVE_RESERVATION_STATUSES,
        ).count()
        return max(0, book.quantity - active_count)

    def _respond(
        self,
        request,
        book,
        level,
        text,
        status_code,
        available_quantity=None,
        redirect_url_name="ReadMe:book_details",
    ):
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

        getattr(messages, level)(request, text)
        return redirect(redirect_url_name, pk=book.pk)

    def post(self, request, pk):
        today = timezone.localdate()
        outcome = None

        with transaction.atomic():
            book = get_object_or_404(Book.objects.select_for_update(), pk=pk)

            active_count = Reservation.objects.filter(
                book=book,
                status__in=ACTIVE_RESERVATION_STATUSES,
            ).count()
            available_before = max(0, book.quantity - active_count)

            if active_count >= book.quantity:
                outcome = ("error", "Réservation impossible : tous les exemplaires actifs sont déjà réservés ou empruntés.", 409, 0)
            else:
                user_active_count = Reservation.objects.filter(
                    user=request.user,
                    status__in=ACTIVE_RESERVATION_STATUSES,
                ).count()

                if user_active_count >= MAX_ACTIVE_RESERVATIONS_PER_USER:
                    outcome = (
                        "error",
                        f"Réservation impossible : vous avez déjà {MAX_ACTIVE_RESERVATIONS_PER_USER} réservations actives (maximum autorisé).",
                        409,
                        available_before,
                    )
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
                        reservation.full_clean()
                        reservation.save()
                    except ValidationError as exc:
                        reason = "; ".join(
                            msg
                            for msgs in (exc.message_dict.values() if hasattr(exc, "message_dict") else [exc.messages])
                            for msg in msgs
                        ) or "La validation de la réservation a échoué."
                        outcome = ("error", f"Réservation impossible : {reason}", 400, available_before)
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

        # Ici, le bloc atomic est terminé : la transaction est propre
        level, text, status_code, avail_qty = outcome
        return self._respond(
            request,
            book,
            level=level,
            text=text,
            status_code=status_code,
            available_quantity=avail_qty,
        )