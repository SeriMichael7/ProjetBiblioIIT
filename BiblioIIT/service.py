"""Logique applicative : relie les règles et le dépôt. Aucun print/input ici."""

from datetime import date
from typing import Callable, List, Tuple

import regles
from depot_sqlite import DepotSQLite
from modeles import Emprunt, Livre


class ErreurBibliotheque(Exception):
    """Erreur métier dont le message peut être affiché tel quel à l'utilisateur."""


class DonneeInvalide(ErreurBibliotheque):
    pass


class LivreIntrouvable(ErreurBibliotheque):
    pass


class LivreDejaEmprunte(ErreurBibliotheque):
    pass


class LimiteEmpruntsAtteinte(ErreurBibliotheque):
    pass


class EmpruntIntrouvable(ErreurBibliotheque):
    pass


class Service:
    def __init__(self, depot: DepotSQLite, aujourdhui: Callable[[], date] = date.today):
        self._depot = depot
        self._aujourdhui = aujourdhui

    def _livre_existant(self, code: str) -> Livre:
        if not regles.code_livre_valide(code):
            raise DonneeInvalide("Code de livre invalide (format attendu : L002).")
        livre = self._depot.trouver_livre(code)
        if livre is None:
            raise LivreIntrouvable(f"Aucun livre ne porte le code {code}.")
        return livre

    def rechercher(self, mot_cle: str) -> List[Livre]:
        if not mot_cle.strip():
            raise DonneeInvalide("Veuillez saisir un mot-clé.")
        return self._depot.rechercher(mot_cle)

    def emprunter(self, code: str, matricule: str) -> Emprunt:
        code, matricule = code.strip().upper(), matricule.strip().upper()
        if not regles.matricule_valide(matricule):
            raise DonneeInvalide("Matricule invalide (format attendu : E2026-001).")
        livre = self._livre_existant(code)
        if not livre.disponible:
            raise LivreDejaEmprunte(f"Le livre « {livre.titre} » est déjà emprunté.")
        if regles.limite_atteinte(self._depot.compter_emprunts_en_cours(matricule)):
            raise LimiteEmpruntsAtteinte(
                f"{matricule} a déjà {regles.MAX_EMPRUNTS_PAR_ETUDIANT} livres empruntés."
            )
        aujourdhui = self._aujourdhui()
        emprunt = Emprunt(code, matricule, aujourdhui, regles.calculer_date_retour(aujourdhui))
        return self._depot.enregistrer_emprunt(emprunt)

    def rendre(self, code: str) -> Tuple[Emprunt, int]:
        """Retourne l'emprunt clôturé et le nombre de jours de retard (0 si à l'heure)."""
        code = code.strip().upper()
        livre = self._livre_existant(code)
        emprunt = self._depot.emprunt_en_cours(code)
        if emprunt is None:
            raise EmpruntIntrouvable(f"Le livre « {livre.titre} » n'est pas emprunté.")
        aujourdhui = self._aujourdhui()
        self._depot.cloturer_emprunt(emprunt.id, aujourdhui)
        emprunt.date_retour_effective = aujourdhui
        return emprunt, regles.jours_de_retard(emprunt.date_retour_prevue, aujourdhui)

    def lister_retards(self) -> List[Tuple[Emprunt, Livre, int]]:
        aujourdhui = self._aujourdhui()
        retards = []
        for emprunt in self._depot.lister_emprunts_en_cours():
            if regles.est_en_retard(emprunt, aujourdhui):
                livre = self._depot.trouver_livre(emprunt.code_livre)
                jours = regles.jours_de_retard(emprunt.date_retour_prevue, aujourdhui)
                retards.append((emprunt, livre, jours))
        return retards
