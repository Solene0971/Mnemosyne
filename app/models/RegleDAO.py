import json
import os

CHAMPS_AUTORISES = {
    "f.annee_but":           "Année BUT (1, 2 ou 3)",
    "i.annee_universitaire": "Année universitaire",
    "i.moyenne":             "Moyenne de l'étudiant",
    "d.acronyme":            "Département",
    "r.acronyme":            "Rythme (FI / FA)",
    "dec.acronyme":          "Décision du jury",
    "dec.nom":               "Libellé décision",
    "et.acronyme":           "État de l'étudiant",
}
OPERATEURS_AUTORISES = {"=", ">", "<", ">=", "<=", "!=", "LIKE"}


class RegleDAO():

    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "..", "static", "data", "regles.json")
        with open(file_path, "r", encoding="utf-8") as f:
            self.regles = json.load(f)

    def save(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, "..", "static", "data", "regles.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.regles, f, indent=4, ensure_ascii=False)

    def ajouter_regle(self, nom, description, champ, operateur, valeur):
        if champ not in CHAMPS_AUTORISES or operateur not in OPERATEURS_AUTORISES:
            raise ValueError(f"Champ '{champ}' ou opérateur '{operateur}' non autorisé")
        self.regles.append({
            "nom": nom,
            "description": description,
            "champ": champ,
            "operateur": operateur,
            "valeur": valeur,
            "statut": True
        })
        self.save()

    def supprimer_regle(self, index):
        if 0 <= index < len(self.regles):
            self.regles.pop(index)
            self.save()

    def modifier_statut(self, index, statut):
        if 0 <= index < len(self.regles):
            self.regles[index]["statut"] = statut
            self.save()

    def get_regles(self):
        return self.regles

    def finSQL(self):
        """Retourne (sql_fragment, params) où sql_fragment utilise des ? et champ/op sont validés."""
        sql_parts = []
        params = []
        for r in self.regles:
            if r.get("statut") is True:
                champ = r.get("champ", "")
                op = r.get("operateur", "")
                valeur = r.get("valeur", "")
                if champ in CHAMPS_AUTORISES and op in OPERATEURS_AUTORISES:
                    sql_parts.append(f"{champ} {op} ?")
                    params.append(valeur)
        if not sql_parts:
            return ("", [])
        return (" AND ".join(sql_parts), params)