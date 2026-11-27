from django.views.generic import TemplateView
from .cross_sell import CrossSellMixin

class ReadMeIndex(CrossSellMixin, TemplateView):
    """
    Render the main ReadMe landing page populated with featured early-edition
    books provided by `CrossSellMixin`.
    """
    template_name = "ReadMe/index.html"
