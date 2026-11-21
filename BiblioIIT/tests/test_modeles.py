import unittest
from datetime import date

from modeles import Emprunt, Livre


class TestModeles(unittest.TestCase):
    def test_affichage_livre(self):
        livre = Livre("L004", "Allah n'est pas obligé", "Ahmadou Kourouma", 2000)
        self.assertEqual(str(livre), "L004 Allah n'est pas obligé — Ahmadou Kourouma (2000)")

    def test_emprunt_en_cours(self):
        e = Emprunt("L001", "E2026-001", date(2026, 10, 1), date(2026, 10, 15))
        self.assertTrue(e.est_en_cours)
        e.date_retour_effective = date(2026, 10, 5)
        self.assertFalse(e.est_en_cours)


if __name__ == "__main__":
    unittest.main()
