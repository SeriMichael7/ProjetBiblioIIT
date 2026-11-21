"""Accès à la base SQLite : seul module qui écrit du SQL."""

import sqlite3
from datetime import date
from typing import List, Optional

from modeles import Emprunt, Livre
from regles import normaliser_texte

_SELECT_LIVRE = """
    SELECT l.code, l.titre, l.auteur, l.annee,
           NOT EXISTS (SELECT 1 FROM emprunts e
                       WHERE e.code_livre = l.code
                         AND e.date_retour_effective IS NULL) AS disponible
    FROM livres l
"""

CATALOGUE_EXEMPLE = [
    Livre("L001", "Les Bouts de bois de Dieu", "Ousmane Sembène", 1960),
    Livre("L002", "Les Soleils des indépendances", "Ahmadou Kourouma", 1968),
    Livre("L003", "Une si longue lettre", "Mariama Bâ", 1979),
    Livre("L004", "Allah n'est pas obligé", "Ahmadou Kourouma", 2000),
    Livre("L005", "Le Monde s'effondre", "Chinua Achebe", 1958),
    Livre("L006", "L'Enfant noir", "Camara Laye", 1953),
    Livre("L007", "Le Vieux Nègre et la médaille", "Ferdinand Oyono", 1956),
    Livre("L008", "Python pour les nuls", "John Paul Mueller", 2019),
]


class DepotSQLite:
    def __init__(self, chemin: str = ":memory:"):
        self._cx = sqlite3.connect(chemin)
        self._cx.row_factory = sqlite3.Row
        self._creer_tables()

    def _creer_tables(self) -> None:
        self._cx.executescript(
            """
            CREATE TABLE IF NOT EXISTS livres (
                code   TEXT PRIMARY KEY,
                titre  TEXT NOT NULL,
                auteur TEXT NOT NULL,
                annee  INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS emprunts (
                id                    INTEGER PRIMARY KEY AUTOINCREMENT,
                code_livre            TEXT NOT NULL REFERENCES livres(code),
                matricule             TEXT NOT NULL,
                date_emprunt          TEXT NOT NULL,
                date_retour_prevue    TEXT NOT NULL,
                date_retour_effective TEXT
            );
            """
        )
        self._cx.commit()

    # ---------- livres ----------
    @staticmethod
    def _en_livre(ligne: sqlite3.Row) -> Livre:
        return Livre(ligne["code"], ligne["titre"], ligne["auteur"],
                     ligne["annee"], bool(ligne["disponible"]))

    def ajouter_livre(self, livre: Livre) -> None:
        try:
            self._cx.execute(
                "INSERT INTO livres (code, titre, auteur, annee) VALUES (?, ?, ?, ?)",
                (livre.code, livre.titre, livre.auteur, livre.annee),
            )
            self._cx.commit()
        except sqlite3.IntegrityError as erreur:
            raise ValueError(f"Le code {livre.code} existe déjà.") from erreur

    def trouver_livre(self, code: str) -> Optional[Livre]:
        ligne = self._cx.execute(_SELECT_LIVRE + " WHERE l.code = ?", (code,)).fetchone()
        return self._en_livre(ligne) if ligne else None

    def lister_livres(self) -> List[Livre]:
        lignes = self._cx.execute(_SELECT_LIVRE + " ORDER BY l.code").fetchall()
        return [self._en_livre(l) for l in lignes]

    def rechercher(self, mot_cle: str) -> List[Livre]:
        """Cherche dans le titre, l'auteur et le code (sans tenir compte des accents/majuscules)."""
        mot = normaliser_texte(mot_cle)
        return [
            livre for livre in self.lister_livres()
            if mot in normaliser_texte(f"{livre.code} {livre.titre} {livre.auteur}")
        ]

    def peupler_si_vide(self) -> None:
        if not self.lister_livres():
            for livre in CATALOGUE_EXEMPLE:
                self.ajouter_livre(livre)

    # ---------- emprunts ----------
    @staticmethod
    def _en_emprunt(ligne: sqlite3.Row) -> Emprunt:
        retour = ligne["date_retour_effective"]
        return Emprunt(
            code_livre=ligne["code_livre"],
            matricule=ligne["matricule"],
            date_emprunt=date.fromisoformat(ligne["date_emprunt"]),
            date_retour_prevue=date.fromisoformat(ligne["date_retour_prevue"]),
            date_retour_effective=date.fromisoformat(retour) if retour else None,
            id=ligne["id"],
        )

    def enregistrer_emprunt(self, emprunt: Emprunt) -> Emprunt:
        curseur = self._cx.execute(
            "INSERT INTO emprunts (code_livre, matricule, date_emprunt, date_retour_prevue) "
            "VALUES (?, ?, ?, ?)",
            (emprunt.code_livre, emprunt.matricule,
             emprunt.date_emprunt.isoformat(), emprunt.date_retour_prevue.isoformat()),
        )
        self._cx.commit()
        emprunt.id = curseur.lastrowid
        return emprunt

    def emprunt_en_cours(self, code_livre: str) -> Optional[Emprunt]:
        ligne = self._cx.execute(
            "SELECT * FROM emprunts WHERE code_livre = ? AND date_retour_effective IS NULL",
            (code_livre,),
        ).fetchone()
        return self._en_emprunt(ligne) if ligne else None

    def compter_emprunts_en_cours(self, matricule: str) -> int:
        return self._cx.execute(
            "SELECT COUNT(*) FROM emprunts WHERE matricule = ? AND date_retour_effective IS NULL",
            (matricule,),
        ).fetchone()[0]

    def cloturer_emprunt(self, id_emprunt: int, date_retour: date) -> None:
        self._cx.execute(
            "UPDATE emprunts SET date_retour_effective = ? WHERE id = ?",
            (date_retour.isoformat(), id_emprunt),
        )
        self._cx.commit()

    def lister_emprunts_en_cours(self) -> List[Emprunt]:
        lignes = self._cx.execute(
            "SELECT * FROM emprunts WHERE date_retour_effective IS NULL ORDER BY date_retour_prevue"
        ).fetchall()
        return [self._en_emprunt(l) for l in lignes]

    def fermer(self) -> None:
        self._cx.close()
