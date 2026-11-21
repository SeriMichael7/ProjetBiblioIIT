import unittest
from datetime import date

import regles
from depot_sqlite import DepotSQLite
from modeles import Livre
from service import (DonneeInvalide, EmpruntIntrouvable, LimiteEmpruntsAtteinte,
                     LivreDejaEmprunte, LivreIntrouvable, Service)


class TestService(unittest.TestCase):
    def setUp(self):
        self.jour = date(2026, 10, 1)
        self.depot = DepotSQLite(":memory:")
        for i in range(1, 6):
            self.depot.ajouter_livre(Livre(f"L00{i}", f"Livre {i}", "Auteur", 2000 + i))
        self.service = Service(self.depot, aujourdhui=lambda: self.jour)

    def test_emprunter(self):
        e = self.service.emprunter("l001", "e2026-001")
        self.assertEqual(e.date_retour_prevue, regles.calculer_date_retour(self.jour))
        self.assertFalse(self.depot.trouver_livre("L001").disponible)

    def test_livre_deja_emprunte(self):
        self.service.emprunter("L001", "E2026-001")
        with self.assertRaises(LivreDejaEmprunte):
            self.service.emprunter("L001", "E2026-002")

    def test_donnees_invalides(self):
        with self.assertRaises(DonneeInvalide):
            self.service.emprunter("L001", "abc")
        with self.assertRaises(DonneeInvalide):
            self.service.emprunter("XX", "E2026-001")
        with self.assertRaises(DonneeInvalide):
            self.service.rechercher("  ")

    def test_livre_introuvable(self):
        with self.assertRaises(LivreIntrouvable):
            self.service.emprunter("L999", "E2026-001")

    def test_limite(self):
        for i in range(1, regles.MAX_EMPRUNTS_PAR_ETUDIANT + 1):
            self.service.emprunter(f"L00{i}", "E2026-001")
        with self.assertRaises(LimiteEmpruntsAtteinte):
            self.service.emprunter("L005", "E2026-001")

    def test_rendre_a_l_heure(self):
        self.service.emprunter("L001", "E2026-001")
        _, jours = self.service.rendre("L001")
        self.assertEqual(jours, 0)
        self.assertTrue(self.depot.trouver_livre("L001").disponible)

    def test_rendre_livre_non_emprunte(self):
        with self.assertRaises(EmpruntIntrouvable):
            self.service.rendre("L001")

    def test_retards(self):
        self.service.emprunter("L001", "E2026-001")
        self.assertEqual(self.service.lister_retards(), [])
        self.jour = date(2026, 10, 20)
        retards = self.service.lister_retards()
        self.assertEqual(len(retards), 1)
        self.assertEqual(retards[0][2], 5)
        _, jours = self.service.rendre("L001")
        self.assertEqual(jours, 5)
        self.assertEqual(self.service.lister_retards(), [])


if __name__ == "__main__":
    unittest.main()
