import unittest
from datetime import date

from console import main
from depot_sqlite import DepotSQLite
from service import Service


def jouer(saisies):
    depot = DepotSQLite(":memory:")
    depot.peupler_si_vide()
    service = Service(depot, aujourdhui=lambda: date(2026, 10, 1))
    it = iter(saisies)
    sorties = []

    def entree(invite=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError

    main(service, entree=entree, sortie=sorties.append)
    return "\n".join(sorties)


class TestConsole(unittest.TestCase):
    def test_session_de_reference(self):
        texte = jouer(["1", "Kourouma", "2", "L002", "E2026-001",
                       "2", "L002", "E2026-002", "0"])
        self.assertIn("L004 Allah n'est pas obligé — Ahmadou Kourouma (2000)", texte)
        self.assertIn("Emprunt enregistré. Retour prévu le 15/10/2026.", texte)
        self.assertIn("Impossible : Le livre « Les Soleils des indépendances » est déjà emprunté.", texte)

    def test_choix_invalide_puis_quitter(self):
        texte = jouer(["9", "0"])
        self.assertIn("Choix invalide", texte)
        self.assertIn("Au revoir", texte)

    def test_rendre_et_retards(self):
        texte = jouer(["2", "L001", "E2026-001", "3", "L001", "4", "0"])
        self.assertIn("Livre rendu", texte)
        self.assertIn("Aucun retard.", texte)

    def test_fin_de_saisie(self):
        texte = jouer([])
        self.assertIn("Au revoir", texte)


if __name__ == "__main__":
    unittest.main()
