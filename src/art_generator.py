"""
🎨 Générateur d'art abstrait basé sur le jeu de données IRIS
- Remplit 100% de l'image (pas d'espace vide)
- Déterministe (même entrée -> même image)
- Si le CSV contient moins de lignes que la grille, on répète les lignes de manière déterministe
"""

import pandas as pd
from PIL import Image, ImageDraw
import sys

WIDTH = 1920
HEIGHT = 1080

GRID_COLS = 15
GRID_ROWS = 10
EXPECTED_CELLS = GRID_COLS * GRID_ROWS

COLOR_PALETTES = {
    'Iris-setosa': [
        (255, 107, 107),
        (255, 159, 128),
        (255, 193, 154)
    ],
    'Iris-versicolor': [
        (78, 205, 196),
        (69, 183, 209),
        (108, 156, 255)
    ],
    'Iris-virginica': [
        (199, 125, 255),
        (162, 155, 254),
        (138, 43, 226)
    ]
}

def normalize(value, min_val, max_val):
    if max_val - min_val == 0:
        return 0.0
    return float(value - min_val) / float(max_val - min_val)

def clamp(value, min_val=0, max_val=255):
    return int(max(min_val, min(value, max_val)))

def ensure_full_grid_df(df):
    """
    Retourne un DataFrame de taille EXACTE EXPECTED_CELLS.
    Si df contient moins de lignes, on répète les lignes (cycle) de façon déterministe.
    Si df contient plus de lignes, on tronque.
    """
    total = len(df)
    if total == 0:
        raise ValueError("Le fichier CSV ne contient aucune ligne utilisable.")
    if total == EXPECTED_CELLS:
        return df.reset_index(drop=True)
    if total > EXPECTED_CELLS:
        return df.iloc[:EXPECTED_CELLS].reset_index(drop=True)

    rows = []
    for i in range(EXPECTED_CELLS):
        rows.append(df.iloc[i % total])
    full = pd.DataFrame(rows).reset_index(drop=True)
    return full

def draw_data_cell(draw, data_row, index, stats):
    """
    Dessine la cellule index (0..EXPECTED_CELLS-1) en recouvrant précisément
    l'aire équivalente. On utilise round pour répartir l'arrondi.
    """
    col = index % GRID_COLS
    row = index // GRID_COLS

    x0 = round(col * WIDTH / GRID_COLS)
    x1 = round((col + 1) * WIDTH / GRID_COLS)
    y0 = round(row * HEIGHT / GRID_ROWS)
    y1 = round((row + 1) * HEIGHT / GRID_ROWS)

    if col == GRID_COLS - 1:
        x1 = WIDTH
    if row == GRID_ROWS - 1:
        y1 = HEIGHT

    n_sepal_len = normalize(data_row['sepal_length'], stats['sepal_length']['min'], stats['sepal_length']['max'])
    n_sepal_wid = normalize(data_row['sepal_width'], stats['sepal_width']['min'], stats['sepal_width']['max'])
    n_petal_len = normalize(data_row['petal_length'], stats['petal_length']['min'], stats['petal_length']['max'])
    n_petal_wid = normalize(data_row['petal_width'], stats['petal_width']['min'], stats['petal_width']['max'])

    palette = COLOR_PALETTES.get(data_row['species'], [(128, 128, 128)] * 3)
    color_index = index % len(palette)
    base_color = palette[color_index]
    r, g, b = base_color

    r = clamp(r * (0.5 + n_sepal_len * 0.5))
    g = clamp(g * (0.5 + n_sepal_wid * 0.5))
    b = clamp(b * (0.5 + n_petal_len * 0.5))

    draw.rectangle([x0, y0, x1, y1], fill=(r, g, b))

def generate_art(data_file, output_file):
    try:
        df = pd.read_csv(data_file)
    except FileNotFoundError:
        print(f"Erreur : fichier introuvable : {data_file}")
        return
    except Exception as e:
        print(f"Erreur en lisant le CSV : {e}")
        return

    sort_cols = ['species', 'sepal_length', 'petal_length', 'petal_width']
    for c in sort_cols:
        if c not in df.columns:
            raise KeyError(f"Colonne manquante dans le CSV : '{c}'")
    df = df.sort_values(by=sort_cols, kind='mergesort').reset_index(drop=True)

    df_full = ensure_full_grid_df(df)

    stats = {
        'sepal_length': {'min': df['sepal_length'].min(), 'max': df['sepal_length'].max()},
        'sepal_width': {'min': df['sepal_width'].min(), 'max': df['sepal_width'].max()},
        'petal_length': {'min': df['petal_length'].min(), 'max': df['petal_length'].max()},
        'petal_width': {'min': df['petal_width'].min(), 'max': df['petal_width'].max()}
    }

    print(f"🖼️ Génération : {len(df_full)} cellules (grille {GRID_COLS}x{GRID_ROWS})")

    img = Image.new('RGB', (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    for index in range(EXPECTED_CELLS):
        row = df_full.iloc[index]
        draw_data_cell(draw, row, index, stats)

    img.save(output_file)
    print(f"✅ Image sauvegardée : {output_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Génère une mosaïque IRIS.")
    parser.add_argument('csv', nargs='?', default='IRIS.csv', help='Fichier CSV input (colonnes : sepal_length, sepal_width, petal_length, petal_width, species)')
    parser.add_argument('out', nargs='?', default='art_mosaique.png', help='Fichier PNG de sortie')
    args = parser.parse_args()
    try:
        generate_art(args.csv, args.out)
    except Exception as exc:
        print("Erreur inattendue :", exc)
        sys.exit(1)
