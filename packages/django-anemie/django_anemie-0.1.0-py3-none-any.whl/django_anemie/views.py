from django.shortcuts import render

def sensibilisation_view(request):
    return render(request, "django_anemie/sensibilisation.html")
