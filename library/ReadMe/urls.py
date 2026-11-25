"""
URL configuration for blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.urls import path
from .views.catalog import BookCatalogView
from .views import ReadMeIndex
from .views.book_details import BookDetailView
from .views.reservation import BookReserveView, ReservationView
from .views.cancel_reservation import cancel_reservation
from .views.manage_reservations import ManageReservationsView, UpdateReservationStatusView
from .views.early_edition import EarlyEdition


app_name = "ReadMe"

urlpatterns = [
    path('', ReadMeIndex.as_view(), name='index'),
    path("catalog/", BookCatalogView.as_view(), name="catalog"),
    path("catalogue/<int:pk>/", BookDetailView.as_view(), name="book_details"),
    path("reservation/<int:pk>/", ReservationView.as_view(), name="reservation"),
    path("reservation/<int:pk>/cancel/", cancel_reservation, name="cancel_reservation"),
    path("books/<int:pk>/reserve/", BookReserveView.as_view(), name="reserve_book"),
    path("manage/reservations/", ManageReservationsView.as_view(), name="manage_reservations"),
    path("manage/reservations/<int:pk>/status/", UpdateReservationStatusView.as_view(), name="update_reservation_status"),
    path("manage/early-edition", EarlyEdition.as_view(), name="early_edition"),
]
