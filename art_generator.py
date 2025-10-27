"""
Générateur d'art abstrait basé sur les données IRIS
Chaque fleur devient une forme géométrique colorée
Résultat déterministe : mêmes données = même image
"""

import pandas as pd
from PIL import Image, ImageDraw
import math
import random

# Paramètres de l'image
WIDTH = 1920
HEIGHT = 1080
BACKGROUND_COLOR = (10, 15, 25)

# Palettes de couleurs par espèce (plus harmonieuses)
COLOR_PALETTES = {
    'Iris-setosa': [
        (255, 107, 107),  # Rouge corail
        (255, 159, 128),  # Pêche
        (255, 193, 154)   # Saumon clair
    ],
    'Iris-versicolor': [
        (78, 205, 196),   # Turquoise
        (69, 183, 209),   # Bleu océan
        (108, 156, 255)   # Bleu pervenche
    ],
    'Iris-virginica': [
        (199, 125, 255),  # Violet
        (162, 155, 254),  # Lavande
        (138, 43, 226)    # Violet bleu
    ]
}

def normalize(value, min_val, max_val, new_min, new_max):
    """Normalise une valeur dans une nouvelle plage"""
    if max_val == min_val:
        return (new_max + new_min) / 2
    return ((value - min_val) / (max_val - min_val)) * (new_max - new_min) + new_min

def get_deterministic_color(species, sepal_length, sepal_width):
    """Retourne une couleur déterministe basée sur les données"""
    palette = COLOR_PALETTES.get(species, [(255, 255, 255)])
    # Index basé sur une combinaison des valeurs (toujours le même pour les mêmes données)
    index = int((sepal_length * 100 + sepal_width * 50)) % len(palette)
    return palette[index]

def draw_flower(draw, row, index, total_rows, stats):
    """Dessine une forme géométrique représentant une fleur"""
    
    # Seed déterministe basé sur les données de la fleur
    seed = int((row['sepal_length'] * 1000 + row['sepal_width'] * 100 + 
                row['petal_length'] * 10 + row['petal_width']))
    random.seed(seed)
    
    # Position : grille avec dispersion déterministe
    grid_x = (index % 15) * (WIDTH / 15)
    grid_y = (index // 15) * (HEIGHT / 10)
    
    # Dispersion basée sur les dimensions des sépales
    offset_x = normalize(row['sepal_length'], stats['sepal_length']['min'], 
                        stats['sepal_length']['max'], -60, 60)
    offset_y = normalize(row['sepal_width'], stats['sepal_width']['min'], 
                        stats['sepal_width']['max'], -60, 60)
    
    x = grid_x + offset_x + 60
    y = grid_y + offset_y + 60
    
    # Taille basée sur la longueur des pétales (plus grande plage)
    size = normalize(row['petal_length'], stats['petal_length']['min'], 
                     stats['petal_length']['max'], 30, 100)
    
    # Nombre de côtés basé sur la largeur des pétales (4 à 12 côtés)
    num_sides = int(normalize(row['petal_width'], stats['petal_width']['min'], 
                              stats['petal_width']['max'], 4, 12))
    
    # Couleur déterministe selon l'espèce et les dimensions
    color = get_deterministic_color(row['species'], row['sepal_length'], row['sepal_width'])
    
    # Rotation déterministe basée sur les données
    rotation = (row['sepal_length'] * row['petal_length'] * 50) % 360
    
    # Calcul des points du polygone
    points = []
    for i in range(num_sides):
        angle = math.radians((360 / num_sides) * i + rotation)
        px = x + size * math.cos(angle)
        py = y + size * math.sin(angle)
        points.append((px, py))
    
    # Opacité basée sur la taille relative (plus cohérent)
    opacity = int(normalize(row['petal_width'], stats['petal_width']['min'], 
                           stats['petal_width']['max'], 150, 220))
    color_with_alpha = color + (opacity,)
    
    # Dessiner un contour léger pour plus de définition
    draw.polygon(points, fill=color_with_alpha, outline=color[:3] + (255,), width=2)

def generate_art():
    """Génère l'œuvre d'art à partir des données IRIS (déterministe)"""
    
    # Reset du générateur aléatoire global (non utilisé mais par sécurité)
    random.seed(42)
    
    # Charger les données
    print("📊 Chargement des données...")
    df = pd.read_csv('IRIS.csv')
    
    # Trier les données pour garantir le même ordre à chaque exécution
    df = df.sort_values(by=['species', 'sepal_length', 'sepal_width', 
                            'petal_length', 'petal_width']).reset_index(drop=True)
    
    # Calculer les statistiques pour la normalisation
    stats = {
        'sepal_length': {'min': df['sepal_length'].min(), 'max': df['sepal_length'].max()},
        'sepal_width': {'min': df['sepal_width'].min(), 'max': df['sepal_width'].max()},
        'petal_length': {'min': df['petal_length'].min(), 'max': df['petal_length'].max()},
        'petal_width': {'min': df['petal_width'].min(), 'max': df['petal_width'].max()}
    }
    
    print(f"🎨 Génération de l'art à partir de {len(df)} fleurs...")
    print("🔒 Mode déterministe : résultat identique garanti")
    
    # Créer l'image avec support de transparence
    img = Image.new('RGBA', (WIDTH, HEIGHT), BACKGROUND_COLOR + (255,))
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Dessiner chaque fleur
    for index, row in df.iterrows():
        draw_flower(draw, row, index, len(df), stats)
    
    # Convertir en RGB pour l'export
    final_img = Image.new('RGB', img.size, BACKGROUND_COLOR)
    final_img.paste(img, mask=img.split()[3])
    
    # Sauvegarder l'image
    output_file = 'iris_art.png'
    final_img.save(output_file, 'PNG')
    
    print(f"✅ Œuvre d'art générée : {output_file}")
    print(f"📐 Dimensions : {WIDTH}x{HEIGHT} pixels")
    print(f"🌸 {len(df)} fleurs transformées en formes géométriques")
    print("🎯 Rendu déterministe : mêmes données = même image")

if __name__ == "__main__":
    generate_art()
