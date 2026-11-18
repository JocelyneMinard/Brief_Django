from django.db import models
from django.db.models import Q  # Q allows you to handle relationships that are more complex than the default “AND” relationship, for filter(), instead of a boolean

class User(models.Model):
    """
    Represents an user of the application ReadMe Library.
    An user can be a simple user or a manager

    Business rules :
        - The email format must be valid
        - The membership number follows the format BIB-XXXX (XXXX is the id in db) and is unique.
    """

    first_name = models.CharField(max_length=150, null=False, help_text="First name of the user")
    last_name = models.CharField(max_length=150, null=False, help_text="Last name of the user")
    mail = models.EmailField(unique=True, null=False, help_text="Mail of the user") 
    role = models.CharField(max_length=50, default='utilisateur', null=False, help_text="Role of the user (user or manager)")

    membership_number = models.CharField(max_length=50, unique=True, blank=True, help_text="Number of membership, unique with the format BIB-XXXX")

    # A native Django class reserved for configuration
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(mail__contains='@'),
                name='check_mail_format'
            ),
        ]

    def save(self, *args, **kwargs)-> None:
        """
        Saves the user instance. 
        For a new user, performs an initial save to obtain an auto-incremented ID, 
        Then generates and saves a unique membership number in the 'BIB-XXXX' format.
        """

        # Check if this is a creation and not an update, pk is the primary key (native from Django)
        is_new = self.pk is None
        # super() allows the creation of the row in the table with save() before the rest of the code
        super().save(*args, **kwargs)

        # Check if this is a creation and if the number is not already created
        if is_new and not self.membership_number:

            # We add the format "BIB-" wanted with the id of the user
            self.membership_number = f"BIB-{self.id:04d}"
 
            super().save(update_fields=['membership_number'])

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.mail})"


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
                check=Q(published_year__gte=1850) & Q(published_year__lte=2025),
                name='check_published_year_range'
            ),
            # Checks to see if the book lists the correct quantities
            models.CheckConstraint(
                check=Q(quantity__gte=1) & Q(quantity__lte=4),
                name='check_quantity_range'
            ),
        ]

    def __str__(self):
        return self.title


class Reservation(models.Model):
    """
    Represents an instance of a book reservation made by a user.

    Business rules :
        - Creation date must be between 2026-09-01 and 2026-22-15
        - An update cannot precede a creation
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, help_text="User who reserved the book")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=False help_text="Book reserved by the user")
    status = models.CharField(max_length=50, default='pending', null=False, help_text="Actual status of the reservation")
    creation_date = models.DateTimeField(null=False, help_text="Date when the reservation was created")
    last_update = models.DateTimeField(blank=True, null=True, help_text="Last update of the reservation")

    # A native Django class reserved for configuration
    class Meta:
        constraints = [
            # Check if the creation_date is between the two mandatory dates
            models.CheckConstraint(
                check=Q(creation_date__gte='2026-09-01') & Q(creation_date__lte='2026-11-15'),
                name='check_creation_date_range'
            ),
            # Check if the update is posterior to the creation
            models.CheckConstraint(
                check=Q(last_update__gte=models.F('creation_date')),
                name='check_status_date_order'
            ),
        ]

    def __str__(self):
        return f"Reservation #{self.id} - {self.user} ({self.status})"