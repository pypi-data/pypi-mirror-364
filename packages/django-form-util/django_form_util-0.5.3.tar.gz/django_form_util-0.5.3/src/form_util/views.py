from django.shortcuts import render
from src.form_util.forms import WelcomeForm

def welcome_view(request):
    form = WelcomeForm()
    return render(request, "form_util/index.html", {"form": form, "user": request.user})
