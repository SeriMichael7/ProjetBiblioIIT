"""Règles métier de BiblioIIT (aucun accès à la base ni à l'écran ici)."""

import re
import unicodedata
from datetime import date, timedelta

from modeles import Emprunt

# --- Paramètres modifiables ---
DUREE_EMPRUNT_JOURS = 14
MAX_EMPRUNTS_PAR_ETUDIANT = 3

_FORMAT_MATRICULE = re.compile(r"^E\d{4}-\d{3}$")   # ex. E2026-001
_FORMAT_CODE_LIVRE = re.compile(r"^L\d{3}$")        # ex. L002


def matricule_valide(matricule: str) -> bool:
    return bool(_FORMAT_MATRICULE.match(matricule))


def code_livre_valide(code: str) -> bool:
    return bool(_FORMAT_CODE_LIVRE.match(code))


def calculer_date_retour(date_emprunt: date) -> date:
    return date_emprunt + timedelta(days=DUREE_EMPRUNT_JOURS)


def est_en_retard(emprunt: Emprunt, aujourdhui: date) -> bool:
    return emprunt.est_en_cours and aujourdhui > emprunt.date_retour_prevue


def jours_de_retard(date_retour_prevue: date, date_reference: date) -> int:
    return max(0, (date_reference - date_retour_prevue).days)


def limite_atteinte(nb_emprunts_en_cours: int) -> bool:
    return nb_emprunts_en_cours >= MAX_EMPRUNTS_PAR_ETUDIANT


def normaliser_texte(texte: str) -> str:
    """Minuscules sans accents, pour une recherche tolérante."""
    decompose = unicodedata.normalize("NFD", texte)
    sans_accents = "".join(c for c in decompose if unicodedata.category(c) != "Mn")
    return sans_accents.casefold().strip()
