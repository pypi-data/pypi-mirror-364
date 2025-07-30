from django.urls import path
from src.form_util.views import welcome_view

urlpatterns = [
    path("", welcome_view, name="form_util"),
]
