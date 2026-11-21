import unittest
from datetime import date

from depot_sqlite import DepotSQLite
from modeles import Emprunt, Livre


class TestDepot(unittest.TestCase):
    def setUp(self):
        self.depot = DepotSQLite(":memory:")
        self.depot.ajouter_livre(Livre("L001", "Une si longue lettre", "Mariama Bâ", 1979))
        self.depot.ajouter_livre(Livre("L002", "Les Soleils des indépendances", "Ahmadou Kourouma", 1968))

    def tearDown(self):
        self.depot.fermer()

    def test_code_en_double(self):
        with self.assertRaises(ValueError):
            self.depot.ajouter_livre(Livre("L001", "Autre", "Quelqu'un", 2000))

    def test_trouver(self):
        self.assertEqual(self.depot.trouver_livre("L002").auteur, "Ahmadou Kourouma")
        self.assertIsNone(self.depot.trouver_livre("L999"))

    def test_recherche_sans_accent_ni_casse(self):
        self.assertEqual([l.code for l in self.depot.rechercher("KOUROUMA")], ["L002"])
        self.assertEqual([l.code for l in self.depot.rechercher("ba")], ["L001"])
        self.assertEqual(self.depot.rechercher("zzz"), [])

    def test_emprunt_et_disponibilite(self):
        e = self.depot.enregistrer_emprunt(
            Emprunt("L002", "E2026-001", date(2026, 10, 1), date(2026, 10, 15)))
        self.assertIsNotNone(e.id)
        self.assertFalse(self.depot.trouver_livre("L002").disponible)
        self.assertEqual(self.depot.compter_emprunts_en_cours("E2026-001"), 1)
        self.depot.cloturer_emprunt(e.id, date(2026, 10, 10))
        self.assertTrue(self.depot.trouver_livre("L002").disponible)
        self.assertIsNone(self.depot.emprunt_en_cours("L002"))

    def test_peupler_si_vide(self):
        autre = DepotSQLite(":memory:")
        autre.peupler_si_vide()
        nb = len(autre.lister_livres())
        autre.peupler_si_vide()
        self.assertEqual(len(autre.lister_livres()), nb)
        self.assertGreater(nb, 0)


if __name__ == "__main__":
    unittest.main()
