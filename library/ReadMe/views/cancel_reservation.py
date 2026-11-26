from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from ..models import Reservation

@login_required
@require_POST
def cancel_reservation(request, pk):
    # take reservation only for the self user
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)

    if reservation.status in ["prete", "en_attente"]:
        reservation.status = "annulee"
        reservation.save(update_fields = ["status", "last_update"])
        messages.success(request, "Votre réservation a bien été annulée.")
    else:
        messages.error(request, "Cette réservation ne peut plus être annulée.")

    # Redirect to user reservation
    return redirect("ReadMe:reservation")