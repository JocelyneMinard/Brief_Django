from cuser.models import AbstractCUser
from django.db import models

class User(AbstractCUser):
    """
    Custom user model for the ReadMe Library system.
    Inherits from AbstractUser to handle authentication while adding library-specific fields.

    Business rules :
        - The membership number follows the format BIB-XXXX (XXXX is the id in db) and is unique.
    """

    role = models.CharField(max_length=50, default='utilisateur', null=False, help_text="Role of the user (user or manager)")

    membership_number = models.CharField(max_length=50, unique=True, blank=True, null=False, help_text="Number of membership, unique with the format BIB-XXXX")


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
        return f"{self.first_name} {self.last_name} ({self.email})"