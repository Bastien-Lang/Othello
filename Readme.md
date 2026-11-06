# Othello — TP Intelligence artificielle

Jeu en console avec humain, MinMax, alpha-bêta ou joueur aléatoire.
Python 3.10 ou plus récent et NumPy sont requis.

## Installation et lancement

Depuis le dossier du projet :

```powershell
python -m pip install -r requirements.txt
python main.py
```

Pour utiliser un environnement isolé sous PowerShell (sans activation nécessaire) :

```powershell
& "$env:LOCALAPPDATA\Python\pythoncore-3.12-64\python.exe" -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe main.py
```

Au lancement, choisissez séparément le joueur noir puis le joueur blanc :

1. Humain
2. MinMax
3. Alpha-bêta
4. Aléatoire

Toutes les combinaisons sont possibles : humain contre IA avec la couleur de
votre choix, deux humains, deux algorithmes différents ou un algorithme contre
lui-même. Les parties entre IA sont automatiques, avec une mémoire propre à chaque IA.

Les Blancs commencent,
conformément au TP. Les cases `*` indiquent les coups autorisés. Saisissez une
coordonnée comme `d3`, puis Entrée. Tapez `q` ou Ctrl+C pour quitter.
Les passes sont automatiques ; le score et le gagnant s'affichent à la fin.

Pour chaque IA, le menu demande une profondeur en demi-coups (Entrée : 2),
puis un budget de temps par coup en secondes (Entrée : 2 ; 0 : sans limite).
Deux demi-coups correspondent à un coup et une réponse, soit la profondeur 1
du TP. Pour comparer les algorithmes, choisissez les mêmes paramètres.
Vous pouvez quitter le menu avec `q`.
Alpha-bêta utilise la même évaluation, mais évite certaines branches inutiles.
Pour simplifier sa mémoire, seules les valeurs exactes sont conservées.
Les bornes obtenues après une coupe ne sont pas enregistrées : cela peut demander
quelques recalculs, sans changer la valeur trouvée à profondeur fixe.
Pour comparer les algorithmes, utilisez la même position et la même profondeur,
sans délai (`time_limit=None`), avec deux moteurs neufs. Les mesures sont dans
`player.last_result.stats` : `nodes`, `cache_hits` et `elapsed_seconds`.

Sous Windows, si `python` pointe sur le Python de WAPT, sélectionnez votre
interpréteur Python 3.10+ dans l'IDE. Sur cette machine, vous pouvez aussi lancer :

```powershell
& "$env:LOCALAPPDATA\Python\pythoncore-3.12-64\python.exe" main.py
```

## Tests

Les tests conservés dans `tests/` couvrent les règles, les parties, les choix du
menu, la justesse des algorithmes, les délais et la mémoire. Ils utilisent des
fonctions simples avec `assert`, exécutées par Pytest :

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Fichiers

- `main.py` : menu de choix des joueurs et lancement de la partie.
- `board.py`, `constants.py` : plateau et règles.
- `game.py` : tours, passes, résultat et sauvegarde de l'historique (texte pour `.txt`, JSON sinon).
- `player.py`, `view.py` : joueurs et interface console.
- `minmax.py` : moteur MinMax utilisé par l'IA.
- `alphabeta.py` : moteur avec élagage alpha-bêta, délai et mémoire des valeurs exactes.
- `search.py` : ancienne version de recherche, non utilisée par le jeu.
- `tests/` : tests du plateau, de MinMax et des parties complètes.
- `pytest.ini` : découverte des tests et imports depuis la racine du projet.
- `requirements.txt`, `requirements-dev.txt` : dépendances du jeu et des tests.

Les autres algorithmes du TP seront ajoutés plus tard.
