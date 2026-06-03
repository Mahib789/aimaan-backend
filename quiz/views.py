from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required(login_url="login")
def quiz_home(request):
    questions = [
        {
            "id": 1,
            "question": "What is phishing?",
            "options": [
                "A cyber attack to steal data",
                "A type of antivirus",
                "A browser update",
                "A game"
            ],
            "answer": "A cyber attack to steal data",
        },
        {
            "id": 2,
            "question": "What should you NEVER share?",
            "options": ["OTP", "Username", "Email", "Phone number"],
            "answer": "OTP",
        },
        {
            "id": 3,
            "question": "Which is a phishing sign?",
            "options": [
                "Urgent message asking login",
                "Official website",
                "Verified app",
                "Bank branch visit"
            ],
            "answer": "Urgent message asking login",
        }
    ]

    return render(request, "quiz.html", {"questions": questions})


@login_required(login_url="login")
def quiz_result(request):

    if request.method != "POST":
        return redirect("quiz_home")   # 🔥 IMPORTANT FIX

    questions = [
        {
            "id": 1,
            "question": "What is phishing?",
            "options": ["A cyber attack to steal data", "A type of antivirus", "A browser update", "A game"],
            "answer": "A cyber attack to steal data",
        },
        {
            "id": 2,
            "question": "What should you NEVER share?",
            "options": ["OTP", "Username", "Email", "Phone number"],
            "answer": "OTP",
        },
        {
            "id": 3,
            "question": "Which is a phishing sign?",
            "options": ["Urgent message asking login", "Official website", "Verified app", "Bank branch visit"],
            "answer": "Urgent message asking login",
        }
    ]

    score = 0
    results = []

    for q in questions:
        selected = request.POST.get(f"q_{q['id']}", "")

        is_correct = selected.strip().lower() == q["answer"].strip().lower()

        if is_correct:
            score += 1

        results.append({
            "question": q["question"],
            "selected": selected,
            "correct": q["answer"],
            "is_correct": is_correct
        })

    return render(request, "result.html", {
        "score": score,
        "total": len(questions),
        "results": results
    })