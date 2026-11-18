# ReadMe Library

Welcome to ReadMe Library, your warm and connected neighborhood library. Come borrow books, study or work in a quiet space, and enjoy cultural moments right around the corner.


## Installation
```pip install -r requierements.txt```

 After this :
 ```
 cd library
 python manage.py migrate
 python manage.py add_data
 python manage.py runserver
 ```

## Technical choices
### dbdiagram
We selected **[dbdiagram.io](https://dbdiagram.io/home)** for database modeling due to its simplicity, zero-install browser interface, and free tier. Using plain-text DBML syntax makes it natively Git-compatible for easy version control, while built-in AI features remain optionally available if needed.

### SQLite
The use of SQLite is directly mandated by the project brief.

### Task management 
https://kabane.spendbaker.com/boards/kabane-tour-3989bb0d/wide

### Structure
Django automatically registers any Python script inside an app's management/commands/ directory as long as it doesn't start with an underscore. **[Django documentation](https://docs.djangoproject.com/en/6.1/howto/custom-management-commands/)