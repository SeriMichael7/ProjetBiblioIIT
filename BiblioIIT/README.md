# BiblioIIT — Gestion de la bibliothèque

Application **console** en Python pour gérer une petite bibliothèque :
rechercher un livre, emprunter, rendre et consulter les retards.
Projet de la séance 4 — Institut Ivoirien de Technologie (IIT).

---

## 1. Prérequis

- **Python 3.9 ou plus récent** (testé avec Python 3.12)
- Aucune bibliothèque externe : `sqlite3` et `unittest` sont déjà inclus dans Python.

Vérifier la version installée :

```
python --version
```

> Sous Windows, si `python` n'est pas reconnu, essayez `py` à la place.
> Sous Linux / macOS, utilisez `python3`.

## 2. Lancer le programme

1. Ouvrir un terminal (PowerShell, CMD ou le terminal de VS Code).
2. Se placer dans le dossier du projet :

   ```
   cd BiblioIIT
   ```

3. Lancer l'application :

   ```
   python console.py
   ```

Au premier lancement, le fichier `biblioiit.db` (la base SQLite) est créé
automatiquement et rempli avec 8 livres d'exemple (codes `L001` à `L008`).

## 3. Utilisation

Le menu s'affiche en boucle. Tapez le numéro de l'action puis **Entrée**.

| Choix | Action | Ce qu'on vous demande |
|-------|--------|-----------------------|
| 1 | Rechercher un livre | un mot-clé (titre, auteur ou code) |
| 2 | Emprunter | le code du livre, puis le matricule |
| 3 | Rendre | le code du livre |
| 4 | Retards | rien : affiche les emprunts en retard |
| 0 | Quitter | — |

Formats attendus :

- **Code du livre** : `L` + 3 chiffres, par exemple `L002`
- **Matricule** : `E` + année + `-` + 3 chiffres, par exemple `E2026-001`

### Exemple de session

```
=== BiblioIIT ===
1. Rechercher un livre   2. Emprunter
3. Rendre                4. Retards   0. Quitter
Votre choix : 1
Mot-clé : Kourouma
  L002 Les Soleils des indépendances — Ahmadou Kourouma (1968)
  L004 Allah n'est pas obligé — Ahmadou Kourouma (2000)
Votre choix : 2
Code du livre : L002
Matricule : E2026-001
Emprunt enregistré. Retour prévu le 03/12/2026.
Votre choix : 2
Code du livre : L002
Matricule : E2026-002
Impossible : Le livre « Les Soleils des indépendances » est déjà emprunté.
Votre choix : 0
Au revoir !
```

## 4. Règles de gestion

Elles sont regroupées dans `regles.py` et faciles à modifier :

| Règle | Valeur par défaut | Constante |
|-------|-------------------|-----------|
| Durée d'un emprunt | 14 jours | `DUREE_EMPRUNT_JOURS` |
| Nombre maximum de livres par étudiant | 3 | `MAX_EMPRUNTS_PAR_ETUDIANT` |

- Un livre déjà emprunté ne peut pas être emprunté une seconde fois.
- Un emprunt est « en retard » quand la date du jour dépasse la date de retour prévue.
- La recherche ignore les majuscules et les accents (`kourouma`, `BA` → `Bâ`).

## 5. Lancer les tests

```
python -m unittest discover -s tests -t . -v
```

Résultat attendu : `OK` (26 tests). Les tests n'utilisent pas le fichier
`biblioiit.db` : ils travaillent sur une base en mémoire.

## 6. Organisation du code

```
BiblioIIT/
├── console.py        # menu et saisies (E) — seul module qui fait print/input
├── service.py        # logique applicative (D) — relie règles et base
├── regles.py         # règles métier (A) — durée, retard, formats, limite
├── modeles.py        # classes Livre et Emprunt (B)
├── depot_sqlite.py   # base SQLite (C) — seul module qui écrit du SQL
├── tests/            # chacun ses tests
├── .github/workflows/ci.yml   # pipeline : lance les tests à chaque push / PR
├── .gitignore
└── README.md
```

Les dépendances vont toujours dans le même sens :

```
console  →  service  →  regles
                    →  depot_sqlite  →  modeles
```

Chaque couche ne connaît que celle du dessous : `console.py` n'écrit jamais de
SQL, et `depot_sqlite.py` n'affiche jamais rien.


