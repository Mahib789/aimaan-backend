from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url="login")
def course_list(request):
    return render(request, "learning.html")