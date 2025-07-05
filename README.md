# FMO_Orca

**FMO_Orca** est un workflow Python modulaire pour automatiser des calculs ORCA à partir de chaînes SMILES, avec génération, exécution et parsing robustes des entrées/sorties.  
Il inclut : conversion SMILES→XYZ, configuration avancée, exécution ORCA, extraction des résultats, logging détaillé et export Markdown.

## Fonctionnalités principales

- Conversion SMILES → géométrie XYZ optimisée (RDKit)
- Génération d'inputs ORCA paramétrés (DFT, sTDA, PIEDA…)
- Exécution automatique d'ORCA avec gestion mémoire/cœurs
- Parsing des sorties (singlet/triplet, fragments…)
- Logging avancé avec traçabilité (run_id, profilage, etc.)
- Résumés prêtes à publier (`results.md`, `.json`)
- CLI ergonomique et fichier de configuration YAML
- Structure modulaire et tests unitaires

## Structure

```
orca_workflow/
├── __init__.py
├── cli.py
├── config.py
├── geometry.py
├── orca_io.py
├── runner.py
├── parser.py
├── workflow.py
└── utils.py
main.py
```

## Installation

1. **RDKit** doit être installé (`conda install -c conda-forge rdkit` recommandé)
2. Installer les dépendances Python :

```bash
pip install -r requirements.txt
```

3. ORCA doit être installé et accessible via le `$PATH` ou explicitement spécifié.

## Usage

### Ligne de commande

```bash
python main.py --smiles "C1=CC..." --molecule_name "4CzIPN"
```

Voir toutes les options :

```bash
python main.py --help
```

### Paramètres par défaut

Les paramètres globaux peuvent être définis via un fichier `config.yaml`.

## Licence

MIT

## Test

Des exemples de tests unitaires sont dans `tests/`.  
Pour exécuter :  
```bash
pytest
```
