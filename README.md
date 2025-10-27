# 🎨 Générateur d'Art Abstrait IRIS

## Description du projet

Ce programme génère automatiquement une œuvre d'art abstraite à partir des données du dataset IRIS (mesures de fleurs). Chaque fleur est transformée en une forme géométrique colorée dont les propriétés visuelles dépendent directement des données.

## 📊 Mapping des données vers l'art

| Donnée | Transformation visuelle |
|--------|------------------------|
| `sepal_length` | Position X (horizontale) |
| `sepal_width` | Position Y (verticale) |
| `petal_length` | Taille de la forme |
| `petal_width` | Nombre de côtés (3-8) |
| `species` | Palette de couleurs |
| Index | Rotation et opacité |

## 🎨 Style artistique

- **Formes** : Polygones géométriques (triangles, carrés, pentagones, hexagones, etc.)
- **Couleurs** : 3 palettes distinctes selon l'espèce de fleur
  - 🔴 Iris-setosa : Tons rouges/roses
  - 🔵 Iris-versicolor : Tons bleus
  - 🟣 Iris-virginica : Tons violets
- **Effet** : Superposition avec opacité progressive

## 📁 Structure du projet

```
artkathon/
├── IRIS.csv              # Données source
├── explore_data.py       # Script d'exploration des données
├── art_generator.py      # Générateur d'art principal
├── iris_art.png          # Image générée (après exécution)
└── README.md            # Documentation
```

## 🚀 Installation

```bash
# Installer les dépendances
sudo apt install python3-pandas python3-pil
```

## ▶️ Utilisation

```bash
# Générer l'œuvre d'art
python3 art_generator.py
```

L'image `iris_art.png` (1920x1080) sera créée dans le répertoire courant.

## 🔧 Personnalisation

Vous pouvez modifier dans `art_generator.py` :
- `WIDTH` et `HEIGHT` : Dimensions de l'image
- `BACKGROUND_COLOR` : Couleur de fond
- `COLOR_PALETTES` : Palettes de couleurs par espèce
- La logique de mapping dans `draw_flower()`

## 📝 Licence

Projet éducatif - Artkathon 2025