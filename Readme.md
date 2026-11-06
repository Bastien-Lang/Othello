# Othello — TP Intelligence artificielle

Jeu en console avec un adversaire MinMax. Python 3.10 ou plus récent et NumPy sont requis.

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

Vous jouez les Noirs (`B`), l'IA joue les Blancs (`W`). Les Blancs commencent,
conformément au TP. Les cases `*` indiquent les coups autorisés. Saisissez une
coordonnée comme `d3`, puis Entrée. Tapez `q` ou Ctrl+C pour quitter.
Les passes sont automatiques ; le score et le gagnant s'affichent à la fin.

Dans `main.py`, `depth=2` examine un coup de l'IA et une réponse adverse
(profondeur 1 selon la convention du TP). `time_limit=2.0` limite la recherche
à environ deux secondes par coup. Le moteur conserve ses analyses entre les tours.

Sous Windows, si `python` pointe sur le Python de WAPT, sélectionnez votre
interpréteur Python 3.10+ dans l'IDE. Sur cette machine, vous pouvez aussi lancer :

```powershell
& "$env:LOCALAPPDATA\Python\pythoncore-3.12-64\python.exe" main.py
```

## Tests

Tous les tests sont regroupés dans `tests/`. Pytest exécute les tests écrits
avec `unittest` ainsi que les nouveaux tests écrits avec `pytest` :

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Fichiers

- `main.py` : configuration et lancement humain contre MinMax.
- `board.py`, `constants.py` : plateau et règles.
- `game.py` : tours, passes, résultat et sauvegarde de l'historique (texte pour `.txt`, JSON sinon).
- `player.py`, `view.py` : joueurs et interface console.
- `minmax.py` : moteur MinMax utilisé par l'IA.
- `search.py` : ancienne version de recherche, non utilisée par le jeu.
- `tests/` : tests du plateau, de MinMax et des parties complètes.
- `pytest.ini` : découverte des tests et imports depuis la racine du projet.
- `requirements.txt`, `requirements-dev.txt` : dépendances du jeu et des tests.

Les autres algorithmes du TP seront ajoutés plus tard.
