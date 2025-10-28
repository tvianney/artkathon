# IRIS Art Generator

## 👥 Équipe

- LEBRETON Benjamin
- SINTONDJI Ange Bignon
- SULTANA Parvin
- SLIMANI Ouassim
- TOUILLON Vianney

## 📖 Description du projet

IRIS Art Generator est un projet qui transforme des données du célèbre dataset IRIS en œuvres d'art abstrait uniques. Le programme utilise les caractéristiques morphologiques des fleurs (longueur et largeur des sépales et pétales) pour générer des compositions visuelles colorées et déterministes.

Chaque donnée est représentée visuellement dans une grille de 15x10 cellules (150 cellules au total). Les couleurs et leur intensité varient selon :
- L'espèce de la fleur (3 palettes de couleurs distinctes)
- Les dimensions des sépales et pétales (modulation de l'intensité RGB)

Le projet propose une interface web intuitive permettant de visualiser, modifier les données et générer instantanément l'art correspondant.

## 📊 Structure du fichier d'entrée

Le programme attend un fichier CSV avec la structure suivante :

```csv
sepal_length,sepal_width,petal_length,petal_width,species
5.1,3.5,1.4,0.2,Iris-setosa
4.9,3.0,1.4,0.2,Iris-setosa
7.0,3.2,4.7,1.4,Iris-versicolor
6.3,3.3,6.0,2.5,Iris-virginica
```

**Colonnes obligatoires :**
- `sepal_length` : Longueur du sépale (nombre décimal)
- `sepal_width` : Largeur du sépale (nombre décimal)
- `petal_length` : Longueur du pétale (nombre décimal)
- `petal_width` : Largeur du pétale (nombre décimal)
- `species` : Espèce de la fleur (texte : `Iris-setosa`, `Iris-versicolor`, ou `Iris-virginica`)

## 🚀 Instructions de lancement

**Prérequis :**
- Docker
- Docker Compose

**Étapes :**

1. **Cloner le projet**
```bash
git clone <url_du_repo>
cd artkathon
```

2. **Construire et lancer le conteneur**
```bash
docker-compose up --build
```

3. **Accéder à l'interface web**
- Ouvrir un navigateur à l'adresse : http://localhost:5001

4. **Arrêter l'application**
```bash
docker-compose down
```

## 🎨 Comment l'art est généré ?

Le programme transforme les données IRIS en art abstrait de manière simple :

1. **Lecture du CSV** : Les données des fleurs sont chargées
2. **Organisation** : Chaque ligne devient une cellule colorée dans une grille de 15×10
3. **Couleurs** : 
   - Chaque espèce de fleur a sa propre palette de couleurs
   - Les dimensions des pétales et sépales influencent l'intensité des couleurs
4. **Génération** : L'image finale est créée et sauvegardée

Le même fichier CSV produira toujours la même œuvre d'art !

## 📁 Structure du projet

```
artkathon/
├── data/              # Données (IRIS.csv fourni)
├── config/            # Configuration (palettes, dimensions)
│   └── settings.py    # Paramètres de génération
├── web_app/           # Application web Flask
│   ├── app.py         # Serveur Flask (API REST)
│   ├── art_engine.py  # Moteur de génération d'art
│   ├── static/        # CSS, JavaScript
│   ├── templates/     # Templates HTML
│   ├── uploads/       # Fichiers CSV temporaires
│   └── outputs/       # Images générées
├── requirements.txt   # Dépendances Python
├── Dockerfile         # Configuration Docker
└── docker-compose.yml # Orchestration Docker
```

## 📎 Fichiers annexes

- **Dockerfile** : Configuration de l'image Docker pour le déploiement
- **docker-compose.yml** : Orchestration des conteneurs avec volumes persistants
- **config/settings.py** : Fichier de configuration centralisant :
  - Dimensions de l'image (WIDTH, HEIGHT)
  - Palettes de couleurs par espèce
  - Paramètres de rendu

## 🛠️ Technologies utilisées

- **Backend** : Python 3.9, Flask
- **Traitement de données** : Pandas, NumPy
- **Génération d'images** : Pillow (PIL)
- **Frontend** : HTML5, CSS3, JavaScript vanilla
- **Déploiement** : Docker, Docker Compose

