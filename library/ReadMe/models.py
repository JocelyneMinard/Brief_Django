from django.db import models
from django.conf import settings
from django.db.models import Q  # Q allows you to handle relationships that are more complex than the default “AND” relationship, for filter(), instead of a boolean
from django.core.exceptions import ValidationError

ACTIVE_RESERVATION_STATUSES = ("en_attente", "prete", "empruntee")

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
        active_count = self.reservation_set.filter(
            status__in=ACTIVE_RESERVATION_STATUSES
        ).count()
        return max(0, (self.quantity or 0) - active_count)


class Reservation(models.Model):
    """
    Represents an instance of a book reservation made by a user.

    Business rules :
        - Creation date must be between 2026-09-01 and 2026-22-15
        - An update cannot precede a creation
    """

    # Use settings.AUTH_USER_MODEL to link reservation and user from django 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text="User who reserved the book")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=False, help_text="Book reserved by the user")
    status = models.CharField(max_length=50, default='pending', null=False, help_text="Actual status of the reservation")
    creation_date = models.DateField(null=False, help_text="Date when the reservation was created")
    last_update = models.DateField(blank=True, null=True, help_text="Last update of the reservation")

    # A native Django class reserved for configuration
    class Meta:
        constraints = [
            # Check if the creation_date is between the two mandatory dates
            models.CheckConstraint(
                condition=Q(creation_date__gte='2026-09-01') & Q(creation_date__lte='2026-11-15'),
                name='check_creation_date_range'
            ),
            # Check if the update is posterior to the creation
            models.CheckConstraint(
                condition=Q(last_update__gte=models.F('creation_date')),
                name='check_status_date_order'
            ),
        ]

    def __str__(self):
        return f"Reservation #{self.id} - {self.user} ({self.status})"

    def clean(self):
        super().clean()
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