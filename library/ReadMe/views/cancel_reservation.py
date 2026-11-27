from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from ..models import Reservation

@login_required
@require_POST
def cancel_reservation(request, pk):
    """
    Cancel a reservation belonging to the currently authenticated user.

    Retrieves the reservation matching `pk` and `request.user`. If its status
    is either 'prete' or 'en_attente', updates the status to 'annulee' and
    displays a success message; otherwise, displays an error message.

    Args:
        request (HttpRequest): The incoming POST HTTP request.
        pk (int): The primary key of the Reservation to cancel.

    Returns:
        HttpResponseRedirect: Redirects to the 'ReadMe:reservation' page.
    """
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)

    if reservation.status in ["prete", "en_attente"]:
        reservation.status = "annulee"
        reservation.save(update_fields = ["status", "last_update"])
        messages.success(request, "Votre réservation a bien été annulée.")
    else:
        messages.error(request, "Cette réservation ne peut plus être annulée.")

    # Redirect to user reservation
    return redirect("ReadMe:reservation")