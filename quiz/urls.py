from django.urls import path
from .views import quiz_home, quiz_result

urlpatterns = [
    path("", quiz_home, name="quiz_home"),
    path("result/", quiz_result, name="quiz_result"),
]