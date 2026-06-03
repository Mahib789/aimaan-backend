import csv
from .models import PredictionFeedback


def export_feedback_to_csv(file_path="feedback.csv"):
    data = PredictionFeedback.objects.all()

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "user",
            "text",
            "predicted_label",
            "safe_prob",
            "fraud_prob",
            "user_feedback",
            "source",
            "created_at"
        ])

        for d in data:
            writer.writerow([
                d.user.username if d.user else "anonymous",
                d.text,
                d.predicted_label,
                d.safe_prob,
                d.fraud_prob,
                d.user_feedback,
                d.source,
                d.created_at
            ])