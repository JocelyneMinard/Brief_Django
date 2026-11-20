from django.views.generic import TemplateView

# Create your views here.
class ReadMeIndex(TemplateView):
    template_name = "ReadMe/index.html"
