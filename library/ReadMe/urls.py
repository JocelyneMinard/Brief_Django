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

app_name = "ReadMe"

urlpatterns = [
    path('', ReadMeIndex.as_view(), name='index'),
    path("catalog/", BookCatalogView.as_view(), name="catalog"),
    path("catalogue/<int:pk>/", BookDetailView.as_view(), name="book_details"),
]
