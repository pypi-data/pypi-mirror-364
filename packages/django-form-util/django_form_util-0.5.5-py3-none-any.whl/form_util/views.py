from django.shortcuts import render
from .forms import WelcomeForm

def welcome_view(request):
    return render(request, "form_util/index.html", {"form": WelcomeForm, "user": request.user})
