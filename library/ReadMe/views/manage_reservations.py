from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.urls import reverse
from urllib.parse import urlencode
from django.views.generic import ListView
from django.db.models import Q

from ..models import Reservation

ALLOWED_TRANSITIONS = {
    "en_attente": {"prete", "annulee"},
    "prete": {"empruntee", "annulee"},
    "empruntee": {"rendue"},
    "rendue": set(),
    "annulee": set(),
}

STATUS_LABELS = {
    "en_attente": "En attente",
    "prete": "Prête",
    "empruntee": "Empruntée",
    "rendue": "Rendue",
    "annulee": "Annulée",
}


class ManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and getattr(user, "role", None) == "gestionnaire"


class ManageReservationsView(ManagerRequiredMixin, ListView):
    model = Reservation
    template_name = "ReadMe/manage_reservations.html"
    context_object_name = "reservations"

    def _get_status_filter(self) -> str:
        status = self.request.GET.get("status","").strip()
        return status if status in STATUS_LABELS else ""

    def _get_user_query(self) -> str:
        return self.request.GET.get("user", "").strip()

    def _get_book_query(self) -> str:
        return self.request.GET.get("book", "").strip()

    def get_queryset(self):
        queryset = (
            Reservation.objects.select_related("user", "book")
            .order_by("-creation_date", "-id")
        )

        selected_status = self._get_status_filter()
        user_query = self._get_user_query()
        book_query = self._get_book_query()

        if selected_status:
            queryset = queryset.filter(status=selected_status)

        if user_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=user_query)
                | Q(user__last_name__icontains=user_query)
                | Q(user__email__icontains=user_query)
                | Q(user__membership_number__icontains=user_query)
            )

        if book_query:
            queryset = queryset.filter(
                Q(book__title__icontains=book_query)
                | Q(book__author__icontains=book_query)
                | Q(book__isbn__icontains=book_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for reservation in context["reservations"]:
            allowed = ALLOWED_TRANSITIONS.get(reservation.status, set())
            reservation.can_mark_prete = "prete" in allowed
            reservation.can_mark_empruntee = "empruntee" in allowed
            reservation.can_mark_rendue = "rendue" in allowed
            reservation.can_cancel = "annulee" in allowed
            reservation.status_label = STATUS_LABELS.get(reservation.status, reservation.status)

        context["status_choices"] = STATUS_LABELS.items()
        context["selected_status"] = self._get_status_filter()
        context["user_query"] = self._get_user_query()
        context["book_query"] = self._get_book_query()
        return context


class UpdateReservationStatusView(ManagerRequiredMixin, View):
    @staticmethod
    def _build_redirect_url(request) -> str:
        base_url = reverse("ReadMe:manage_reservations")
        raw_status = request.POST.get("status", "").strip()
        raw_user = request.POST.get("user", "").strip()
        raw_book = request.POST.get("book", "").strip()

        active_filters = {}
        if raw_status in STATUS_LABELS:
            active_filters["status"] = raw_status
        if raw_user:
            active_filters["user"] = raw_user
        if raw_book:
            active_filters["book"] = raw_book

        if not active_filters:
            return base_url
        return f"{base_url}?{urlencode(active_filters)}"

    def post(self, request, pk):
        redirect_url = self._build_redirect_url(request)
        new_status = request.POST.get("new_status", "").strip()
        reservation = get_object_or_404(Reservation, pk=pk)
        allowed_next = ALLOWED_TRANSITIONS.get(reservation.status, set())

        if new_status not in allowed_next:
            messages.error(
                request,
                f"Transition interdite de « {reservation.status} » vers « {new_status} ».",
            )
            return redirect(redirect_url)

        reservation.status = new_status
        reservation.last_update = timezone.localdate()

        try:
            reservation.full_clean()
            reservation.save(update_fields=["status", "last_update"])
        except Exception as exc:
            messages.error(request, f"Mise à jour impossible : {exc}")
            return redirect(redirect_url)

        messages.success(
            request,
            f"Réservation #{reservation.pk} passée au statut « {STATUS_LABELS.get(new_status, new_status)} ».",
        )
        return redirect(redirect_url)