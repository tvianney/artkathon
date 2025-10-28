# IRIS Art Generator

Générateur d'art abstrait basé sur le dataset IRIS. Transforme les données en œuvres visuelles uniques.

## Structure du projet

```
artkathon/
├── data/              # Données (IRIS.csv)
├── src/               # Scripts Python utilitaires
├── docs/              # Documentation
├── config/            # Fichiers de configuration
├── web_app/           # Application web Flask
│   ├── app.py         # Serveur Flask
│   ├── art_engine.py  # Moteur de génération d'art
│   ├── static/        # CSS, JS, assets
│   ├── templates/     # Templates HTML
│   ├── uploads/       # Fichiers temporaires
│   └── outputs/       # Images générées
└── requirements.txt   # Dépendances Python
```

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
cd web_app
python3 app.py
```

Ouvrez votre navigateur sur http://localhost:5000

## Utilisation

1. Les données IRIS se chargent automatiquement
2. Modifiez les valeurs dans le tableau si besoin
3. Cliquez sur "Générer l'art"
4. Téléchargez votre œuvre unique

## Technologies

- Python 3.x
- Flask
- Pillow (PIL)
- Pandas
