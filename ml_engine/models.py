from django.db import models
from django.contrib.auth.models import User

class PredictionFeedback(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    text = models.TextField()

    predicted_label = models.CharField(
        max_length=10
    )

    safe_prob = models.FloatField()

    fraud_prob = models.FloatField()

    user_feedback = models.CharField(
        max_length=10,
        choices=[
            ("correct", "Correct"),
            ("wrong", "Wrong")
        ]
    )

    comment = models.TextField(
        blank=True,
        null=True
    )

    source = models.CharField(
        max_length=10,
        default="text"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.predicted_label} - "
            f"{self.user_feedback}"
        )