from flask import Flask, render_template, request
from datetime import date, timedelta

app = Flask(__name__)

TAUX = 12.65 * 0.78

jours_semaine = {
    0: "lun", 1: "mar", 2: "mer",
    3: "jeu", 4: "ven", 5: "sam", 6: "dim"
}

@app.route("/", methods=["GET", "POST"])
def index():

    calendrier = []
    resultat = None

    if request.method == "POST":

        action = request.form.get("action")

        annee = int(request.form["annee"])
        mois = int(request.form["mois"])
	treizieme = request.form.get("treizieme")
        j_deb = int(request.form["jour_debut"])
        j_fin = int(request.form["jour_fin"])

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

            total_final = m_base + m_nuit + m_maj + prime
		if treizieme:
    		total_final *= 2

            resultat = {
                "base": round(m_base, 2),
                "nuit": round(m_nuit, 2),
                "maj": round(m_maj, 2),
                "prime": round(prime, 2),
                "total": round(total_final, 2)
		"treizieme": bool(treizieme)
            }

    return render_template(
    "index.html",
    calendrier=calendrier,
    resultat=resultat,
    form_data=request.form
)

if __name__ == "__main__":
    app.run()