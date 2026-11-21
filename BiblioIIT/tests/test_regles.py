import unittest
from datetime import date

import regles
from modeles import Emprunt


class TestRegles(unittest.TestCase):
    def test_matricule(self):
        self.assertTrue(regles.matricule_valide("E2026-001"))
        self.assertFalse(regles.matricule_valide("2026-001"))
        self.assertFalse(regles.matricule_valide("E2026001"))

    def test_code_livre(self):
        self.assertTrue(regles.code_livre_valide("L002"))
        self.assertFalse(regles.code_livre_valide("L2"))

    def test_date_retour(self):
        self.assertEqual(regles.calculer_date_retour(date(2026, 10, 1)), date(2026, 10, 15))

    def test_retard(self):
        e = Emprunt("L001", "E2026-001", date(2026, 10, 1), date(2026, 10, 15))
        self.assertFalse(regles.est_en_retard(e, date(2026, 10, 15)))
        self.assertTrue(regles.est_en_retard(e, date(2026, 10, 16)))
        e.date_retour_effective = date(2026, 10, 16)
        self.assertFalse(regles.est_en_retard(e, date(2026, 10, 20)))

    def test_jours_de_retard(self):
        self.assertEqual(regles.jours_de_retard(date(2026, 10, 15), date(2026, 10, 18)), 3)
        self.assertEqual(regles.jours_de_retard(date(2026, 10, 15), date(2026, 10, 10)), 0)

    def test_limite(self):
        self.assertFalse(regles.limite_atteinte(regles.MAX_EMPRUNTS_PAR_ETUDIANT - 1))
        self.assertTrue(regles.limite_atteinte(regles.MAX_EMPRUNTS_PAR_ETUDIANT))

    def test_normaliser(self):
        self.assertEqual(regles.normaliser_texte("  Bâ Éléphant "), "ba elephant")


if __name__ == "__main__":
    unittest.main()
