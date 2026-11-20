from django.shortcuts import render
from django.contrib.auth import get_user_model

from django.views.generic import TemplateView

# Create your views here.
class ReadMeIndex(TemplateView):
    template_name = "ReadMe/index.html"