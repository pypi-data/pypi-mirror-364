document.getElementById("health-form").addEventListener("submit", function(event) {
    const age = document.getElementById("age").value;
    const systolic = document.getElementById("systolic_bp").value;
    const diastolic = document.getElementById("diastolic_bp").value;

    if (age < 1 || systolic < 50 || diastolic < 30) {
        event.preventDefault();
        alert("Veuillez entrer des valeurs valides pour l'âge et la tension.");
    }
});
