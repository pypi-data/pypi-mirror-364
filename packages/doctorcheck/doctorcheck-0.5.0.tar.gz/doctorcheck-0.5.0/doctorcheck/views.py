from django.shortcuts import render
from .health_logic import evaluate_health

def health_check_view(request):
    result = None
    if request.method == "POST":
        try:
            age = int(request.POST.get("age", 0))
            systolic_bp = int(request.POST.get("systolic_bp", 0))
            diastolic_bp = int(request.POST.get("diastolic_bp", 0))
            has_headache = request.POST.get("has_headache") == "on"
            has_fatigue = request.POST.get("has_fatigue") == "on"

            # Évaluation de la santé
            result = evaluate_health(age, systolic_bp, diastolic_bp, has_headache, has_fatigue)
        except ValueError:
            result = "Veuillez entrer des valeurs numériques valides pour l'âge et la tension."

    return render(request, "health_check.html", {"result": result})
