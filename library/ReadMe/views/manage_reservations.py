from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

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

    def get_queryset(self):
        return (
            Reservation.objects.select_related("user", "book")
            .order_by("-creation_date", "-id")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for reservation in context["reservations"]:
            allowed = ALLOWED_TRANSITIONS.get(reservation.status, set())
            reservation.can_mark_prete = "prete" in allowed
            reservation.can_mark_empruntee = "empruntee" in allowed
            reservation.can_mark_rendue = "rendue" in allowed
            reservation.can_cancel = "annulee" in allowed
            reservation.status_label = STATUS_LABELS.get(reservation.status, reservation.status)
        return context


class UpdateReservationStatusView(ManagerRequiredMixin, View):
    def post(self, request, pk):
        new_status = request.POST.get("status", "").strip()
        reservation = get_object_or_404(Reservation, pk=pk)
        allowed_next = ALLOWED_TRANSITIONS.get(reservation.status, set())

        if new_status not in allowed_next:
            messages.error(
                request,
                f"Transition interdite de « {reservation.status} » vers « {new_status} ».",
            )
            return redirect("ReadMe:manage_reservations")

        reservation.status = new_status
        reservation.last_update = timezone.localdate()

        try:
            reservation.full_clean()
            reservation.save(update_fields=["status", "last_update"])
        except ValidationError as exc:
            reason = "; ".join(
                msg
                for msgs in (exc.message_dict.values() if hasattr(exc, "message_dict") else [exc.messages])
                for msg in msgs
            )
            messages.error(request, f"Mise à jour impossible : {reason}")
            return redirect("ReadMe:manage_reservations")

        messages.success(
            request,
            f"Réservation #{reservation.pk} passée au statut « {STATUS_LABELS.get(new_status, new_status)} ».",
        )
        return redirect("ReadMe:manage_reservations")