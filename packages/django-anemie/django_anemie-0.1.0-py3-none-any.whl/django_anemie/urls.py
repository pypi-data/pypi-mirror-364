from django.urls import path
from .views import sensibilisation_view

urlpatterns = [
    path("anemie/", sensibilisation_view, name="sensibilisation_anemie"),
]
