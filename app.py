from flask import Flask, render_template, request
from datetime import date, timedelta
import os

app = Flask(__name__)

TAUX = 12.65 * 0.78
TAUX_CSG_CRDS_NON_DEDUCTIBLE = 0.029

jours_semaine = {
    0: "lun", 1: "mar", 2: "mer",
    3: "jeu", 4: "ven", 5: "sam", 6: "dim"
}


@app.route("/", methods=["GET", "POST"])
def index():

    calendrier = []
    resultat = None
    form_data = request.form if request.method == "POST" else {}

    if request.method == "POST":

        action = request.form.get("action")

        annee = int(request.form["annee"])
        mois = int(request.form["mois"])
        treizieme = request.form.get("treizieme")
        j_deb = int(request.form["jour_debut"])
        j_fin = int(request.form["jour_fin"])

        # mois précédent
        if mois == 1:
            annee_prec = annee - 1
            mois_prec = 12
        else:
            annee_prec = annee
            mois_prec = mois - 1

        date_debut = date(annee_prec, mois_prec, j_deb)
        date_fin = date(annee, mois, j_fin)

        current = date_debut

        while current <= date_fin:
            code = f"{jours_semaine[current.weekday()]}{current.day:02d}"
            calendrier.append(code)
            current += timedelta(days=1)

        # ======================
        # CALCUL SALAIRE
        # ======================
        if action == "calculer":

            total_heures = 0

            for code in calendrier:
                heures = float(request.form.get(code, 0))
                total_heures += heures

            h_apres21 = float(request.form.get("apres21", 0))
            prime = float(request.form.get("prime", 0))

            m_base = total_heures * TAUX
            m_nuit = h_apres21 * (TAUX * 0.20)

            code_maj = request.form.get("jour_maj")
            pourcent = request.form.get("pourcentage")

            m_maj = 0
            if code_maj and pourcent:
                heures_jour = float(request.form.get(code_maj, 0))
                m_maj = (heures_jour * TAUX) * (float(pourcent) / 100)

            # Salaire brut simulé
            total_brut_simule = m_base + m_nuit + m_maj + prime

            # Déduction CSG/CRDS non déductible
            csg_crds = total_brut_simule * TAUX_CSG_CRDS_NON_DEDUCTIBLE

            total_final = total_brut_simule - csg_crds

            # 13ème mois
            if treizieme:
                total_final *= 2

            resultat = {
                "base": round(m_base, 2),
                "nuit": round(m_nuit, 2),
                "maj": round(m_maj, 2),
                "prime": round(prime, 2),
                "csg_crds": round(csg_crds, 2),
                "treizieme": bool(treizieme),
                "total": round(total_final, 2)
            }

    return render_template(
        "index.html",
        calendrier=calendrier,
        resultat=resultat,
        form_data=form_data
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)