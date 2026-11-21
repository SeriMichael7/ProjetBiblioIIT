"""Interface console de BiblioIIT. Lancer avec : python console.py"""

import os
from datetime import date

from depot_sqlite import DepotSQLite
from service import ErreurBibliotheque, Service

CHEMIN_BASE = os.environ.get(
    "BIBLIOIT_DB", os.path.join(os.path.dirname(os.path.abspath(__file__)), "biblioiit.db")
)

MENU = (
    "\n=== BiblioIIT ===\n"
    "1. Rechercher un livre   2. Emprunter\n"
    "3. Rendre                4. Retards   0. Quitter"
)


def formater_date(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def _rechercher(service, entree, sortie):
    mot = entree("Mot-clé : ")
    livres = service.rechercher(mot)
    if not livres:
        sortie("Aucun livre trouvé.")
    for livre in livres:
        etat = "" if livre.disponible else "  [emprunté]"
        sortie(f"  {livre}{etat}")


def _emprunter(service, entree, sortie):
    code = entree("Code du livre : ")
    matricule = entree("Matricule : ")
    emprunt = service.emprunter(code, matricule)
    sortie(f"Emprunt enregistré. Retour prévu le {formater_date(emprunt.date_retour_prevue)}.")


def _rendre(service, entree, sortie):
    code = entree("Code du livre : ")
    _, jours = service.rendre(code)
    if jours:
        sortie(f"Livre rendu avec {jours} jour(s) de retard.")
    else:
        sortie("Livre rendu. Merci !")


def _retards(service, entree, sortie):
    retards = service.lister_retards()
    if not retards:
        sortie("Aucun retard.")
    for emprunt, livre, jours in retards:
        sortie(f"  {livre.code} {livre.titre} — {emprunt.matricule} : "
               f"{jours} jour(s) de retard (prévu le {formater_date(emprunt.date_retour_prevue)})")


ACTIONS = {"1": _rechercher, "2": _emprunter, "3": _rendre, "4": _retards}


def main(service=None, entree=input, sortie=print) -> None:
    if service is None:
        depot = DepotSQLite(CHEMIN_BASE)
        depot.peupler_si_vide()
        service = Service(depot)
    try:
        while True:
            sortie(MENU)
            choix = entree("Votre choix : ").strip()
            if choix == "0":
                sortie("Au revoir !")
                return
            action = ACTIONS.get(choix)
            if action is None:
                sortie("Choix invalide, tapez 0, 1, 2, 3 ou 4.")
                continue
            try:
                action(service, entree, sortie)
            except ErreurBibliotheque as erreur:
                sortie(f"Impossible : {erreur}")
    except (EOFError, KeyboardInterrupt):
        sortie("\nAu revoir !")


if __name__ == "__main__":
    main()
