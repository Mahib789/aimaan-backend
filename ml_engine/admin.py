import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.db.models import Count

from .models import PredictionFeedback


@admin.register(PredictionFeedback)
class FeedbackAdmin(admin.ModelAdmin):

    # =========================
    # TABLE VIEW
    # =========================
    list_display = (
        "id",
        "user",
        "predicted_label",
        "user_feedback",
        "safe_prob",
        "fraud_prob",
        "source",
        "created_at"
    )

    list_filter = (
        "user_feedback",
        "predicted_label",
        "source",
        "created_at",
    )

    search_fields = (
        "text",
        "user__username",
        "predicted_label",
    )

    ordering = ("-created_at",)

    # =========================
    # ACTIONS (EXPORT CSV)
    # =========================
    actions = ["export_as_csv"]

    def export_as_csv(self, request, queryset):

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="aimaan_feedback.csv"'

        writer = csv.writer(response)

        # header
        writer.writerow([
            "ID",
            "User",
            "Text",
            "Predicted Label",
            "Safe Probability",
            "Fraud Probability",
            "User Feedback",
            "Source",
            "Created At"
        ])

        # data
        for obj in queryset:
            writer.writerow([
                obj.id,
                obj.user.username if obj.user else "Anonymous",
                obj.text,
                obj.predicted_label,
                obj.safe_prob,
                obj.fraud_prob,
                obj.user_feedback,
                obj.source,
                obj.created_at
            ])

        return response

    export_as_csv.short_description = "📥 Export selected as CSV"

    # =========================
    # ADMIN STATS PANEL
    # =========================
    def changelist_view(self, request, extra_context=None):

        extra_context = extra_context or {}

        total = PredictionFeedback.objects.count()
        fraud = PredictionFeedback.objects.filter(predicted_label="FRAUD").count()
        correct = PredictionFeedback.objects.filter(user_feedback="correct").count()
        wrong = PredictionFeedback.objects.filter(user_feedback="wrong").count()

        accuracy = (correct / total * 100) if total else 0

        extra_context["summary"] = {
            "total": total,
            "fraud": fraud,
            "correct": correct,
            "wrong": wrong,
            "accuracy": round(accuracy, 2),
        }

        return super().changelist_view(request, extra_context=extra_context)