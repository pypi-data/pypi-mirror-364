from django.urls import path
from . import views

app_name = "doctorcheck"
urlpatterns = [
    path("", views.health_check_view, name="health_check"),
]
