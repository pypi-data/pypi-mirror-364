from django.shortcuts import render
from .forms import WelcomeForm

def welcome_view(request):
    form = WelcomeForm()
    return render(request, "welcome_form/index.html", {"form": form, "user": request.user})
