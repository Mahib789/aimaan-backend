from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    text = models.TextField()

    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)

    correct_option = models.CharField(
        max_length=10,
        choices=[
            ("1", "Option 1"),
            ("2", "Option 2"),
            ("3", "Option 3"),
            ("4", "Option 4"),
        ]
    )

    explanation = models.TextField()

    def __str__(self):
        return self.text[:50]


class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    total = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)