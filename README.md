# ReadMe Library

Welcome to ReadMe Library, your warm and connected neighborhood library. Come borrow books, study or work in a quiet space, and enjoy cultural moments right around the corner.


## Installation
```pip install -r requierements.txt```

 After this :
 ```
 cd library
 python manage.py migrate
 python manage.py runserver
 ```



## Technical choices
### dbdiagram
We selected **[dbdiagram.io](https://dbdiagram.io/home)** for database modeling due to its simplicity, zero-install browser interface, and free tier. Using plain-text DBML syntax makes it natively Git-compatible for easy version control, while built-in AI features remain optionally available if needed.

### SQLite
The use of SQLite is directly mandated by the project brief.