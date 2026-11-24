from django.views.generic import TemplateView
from .cross_sell import CrossSellMixin

# Create your views here.
class ReadMeIndex(CrossSellMixin, TemplateView):
    template_name = "ReadMe/index.html"
