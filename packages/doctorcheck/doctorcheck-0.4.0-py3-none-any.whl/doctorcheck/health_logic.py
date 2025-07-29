def evaluate_health(age, systolic_bp, diastolic_bp, has_headache, has_fatigue):
    """
    Évalue la santé basée sur la tension artérielle et les symptômes.
    Retourne un message indiquant si l'utilisateur doit consulter un médecin.
    """
    # Plages de tension artérielle (indicatives, non médicalement précises)
    if systolic_bp > 180 or diastolic_bp > 120:
        return "Hypertension sévère détectée. Consultez un médecin immédiatement."
    elif systolic_bp > 140 or diastolic_bp > 90:
        return "Hypertension modérée. Une consultation médicale est recommandée."
    elif systolic_bp < 90 or diastolic_bp < 60:
        return "Tension basse détectée. Consultez un médecin pour évaluation."
    
    # Vérification des symptômes
    if has_headache and has_fatigue:
        return "Symptômes préoccupants (maux de tête et fatigue). Consultez un médecin."
    elif has_headache or has_fatigue:
        return "Symptômes modérés. Surveillez votre état et consultez si cela persiste."
    
    return "Votre santé semble normale basée sur les informations fournies."
