from django.views.generic import ListView

from ..models import Reservation


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