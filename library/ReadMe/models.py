from django.db import models
from django.conf import settings
# Q allows us to handle relationships that are more complex than the default “AND” relationship, for filter(), instead of a boolean
# F allows us to compare two targeted columns even when we don't use the correct column (for example comparing two dates using column_1_date and column_2_id, F will go search for column_2_date)
from django.db.models import Q,F  
from django.core.exceptions import ValidationError
from datetime import date, timezone
from typing import Any

ACTIVE_RESERVATION_STATUSES = ("en_attente", "prete", "empruntee")
MAX_ACTIVE_RESERVATIONS_PER_USER = 3

class Category(models.Model):
    """
    Represents a category, the physical location where the book is found
    """

    name = models.CharField(max_length=100, null=False, help_text="Name of the category")

    def __str__(self):
        return self.name


class Book(models.Model):
    """
    Represents a book available in the ReadMe library catalog.
        
    Business rules:
        - The publication year must be between 1850 and 2025.
        - The number of copies in stock must be between 1 and 4.
    """

    title = models.CharField(max_length=255, null=False, help_text="Full title of the book")
    author = models.CharField(max_length=255, null=False, help_text="Author of the book")
    published_year = models.IntegerField(null=False, help_text="Publication date of the book")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False, help_text="Category where the book is stocked")
    summary = models.TextField(blank=True, null=True, help_text="Summary of the book")
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True, help_text="Official isbn of the book")
    quantity = models.IntegerField(null=False, help_text="Number of copies of the book")
    early_edition = models.BooleanField(null=True, help_text="Early edition selection")

    # A native Django class reserved for configuration
    class Meta:
        constraints = [
            # Checks whether the book falls within the publication period
            models.CheckConstraint(
                condition=Q(published_year__gte=1850) & Q(published_year__lte=2025),
                name='check_published_year_range'
            ),
            # Checks to see if the book lists the correct quantities
            models.CheckConstraint(
                condition=Q(quantity__gte=1) & Q(quantity__lte=4),
                name='check_quantity_range'
            ),
        ]

    def __str__(self):
        return self.title

    @property
    def available_quantity(self) -> int:
        """
        Check the number of available copies by soustracting the quantity of copies by the count of active reservations
        """
        active_count = self.reservation_set.filter(
            status__in=ACTIVE_RESERVATION_STATUSES
        ).count()
        return max(0, (self.quantity or 0) - active_count)


class Reservation(models.Model):
    """
    Represent the reservation of a book by an user.

    Business rules :
- an user can only have 3 active reservations
- the creation date must be between 01-09-2026 and 31-12-2027
- every update must be dated after the creation date
    """

    # User who made the reservation
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="User who reserved the book",
    )
    # Target book being reserved
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        null=False,
        help_text="Book reserved by the user",
    )
    # Workflow state (e.g., pending, approved, cancelled)
    status = models.CharField(
        max_length=50,
        default="en_attente",
        null=False,
        help_text="Actual status of the reservation",
    )
    # Date the reservation was initially created
    creation_date = models.DateField(
        null=False,
        help_text="Date when the reservation was created",
    )
    # Timestamp/date of the most recent status or record update
    last_update = models.DateField(
        blank=True,
        null=True,
        help_text="Last update of the reservation",
    )

    class Meta:
        # Database-level check constraints enforced by SQLite/Django migrations.
        constraints = [
            models.CheckConstraint(
                condition=Q(creation_date__gte=date(2026, 9, 1))
                & Q(creation_date__lte=date(2027, 12, 31)),
                name="check_creation_date_range",
            ),
            models.CheckConstraint(
                condition=Q(last_update__isnull=True)
                | Q(last_update__gte=F("creation_date")),
                name="check_status_date_order",
            ),
        ]

    def __str__(self) -> str:
        """
        Return a readable string representation for admin and debugging
        """
        return f"Reservation #{self.id} - {self.user} ({self.status})"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize last_update on new records before persisting to the database
        """
        # Default last_update to creation_date (or today's local date) when creating a new row
        if self._state.adding and self.last_update is None:
            self.last_update = self.creation_date or timezone.localdate()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        """
        Validate date ordering, per-user active reservation cap, and book stock limits
        """
        super().clean()

        # Ensure last_update never precedes creation_date.
        if self.creation_date and self.last_update and self.last_update < self.creation_date:
            raise ValidationError(
                {"last_update": "La date de mise à jour ne peut pas être antérieure à la date de création."}
            )

        # Enforce the maximum number of concurrent active reservations per user
        if self.user_id and self.status in ACTIVE_RESERVATION_STATUSES:
            user_active_qs = Reservation.objects.filter(
                user_id=self.user_id,
                status__in=ACTIVE_RESERVATION_STATUSES,
            )
            # Exclude the current instance when updating an existing reservation
            if self.pk:
                user_active_qs = user_active_qs.exclude(pk=self.pk)

            if user_active_qs.count() >= MAX_ACTIVE_RESERVATIONS_PER_USER:
                raise ValidationError(
                    f"Vous avez déjà atteint la limite de {MAX_ACTIVE_RESERVATIONS_PER_USER} réservations actives."
                )

        # Prevent over-reserving a book beyond its available copy quantity
        if self.book_id and self.status in ACTIVE_RESERVATION_STATUSES:
            active_qs = Reservation.objects.filter(
                book_id=self.book_id,
                status__in=ACTIVE_RESERVATION_STATUSES,
            )
            if self.pk:
                active_qs = active_qs.exclude(pk=self.pk)

            if active_qs.count() >= self.book.quantity:
                raise ValidationError(
                    "Ce livre a déjà atteint son nombre maximum de réservations actives."
                )