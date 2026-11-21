"""Modèles de données de BiblioIIT : un livre et un emprunt."""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Livre:
    code: str
    titre: str
    auteur: str
    annee: int
    disponible: bool = True

    def __str__(self) -> str:
        return f"{self.code} {self.titre} — {self.auteur} ({self.annee})"


@dataclass
class Emprunt:
    code_livre: str
    matricule: str
    date_emprunt: date
    date_retour_prevue: date
    date_retour_effective: Optional[date] = None
    id: Optional[int] = None

    @property
    def est_en_cours(self) -> bool:
        """Un emprunt est en cours tant que le livre n'a pas été rendu."""
        return self.date_retour_effective is None
