"""
🎨 Générateur d'art abstrait basé sur le jeu de données IRIS
- S'adapte automatiquement à la taille du dataset
- Remplit 100% de l'image (pas d'espace vide)
- Déterministe (même entrée -> même image)
- Calcule la grille exacte en fonction du nombre de lignes
"""

import pandas as pd
from PIL import Image, ImageDraw
import sys
import math
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config.settings import WIDTH, HEIGHT, COLOR_PALETTES


class ArtGenerator:
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width = width
        self.height = height
        self.color_palettes = COLOR_PALETTES
    
    def calculate_optimal_grid(self, num_cells):
        """
        Calcule la grille optimale (cols, rows) pour un nombre de cellules donné.
        La grille contiendra EXACTEMENT num_cells (pas plus).
        """
        target_ratio = self.width / self.height
        best_cols, best_rows = num_cells, 1
        best_diff = float('inf')
        
        for cols in range(1, num_cells + 1):
            if num_cells % cols == 0:
                rows = num_cells // cols
                ratio = cols / rows
                diff = abs(ratio - target_ratio)
                
                if diff < best_diff:
                    best_diff = diff
                    best_cols = cols
                    best_rows = rows
        
        return best_cols, best_rows
    
    def normalize(self, value, min_val, max_val):
        """Normalise une valeur entre 0 et 1"""
        if max_val - min_val == 0:
            return 0.0
        return float(value - min_val) / float(max_val - min_val)
    
    def clamp(self, value, min_val=0, max_val=255):
        """Limite une valeur entre min_val et max_val"""
        return int(max(min_val, min(value, max_val)))
    
    def draw_data_cell(self, draw, data_row, index, grid_cols, grid_rows, stats):
        """
        Dessine la cellule à l'index donné dans la grille
        """
        col = index % grid_cols
        row = index // grid_cols
        
        x0 = round(col * self.width / grid_cols)
        x1 = round((col + 1) * self.width / grid_cols)
        y0 = round(row * self.height / grid_rows)
        y1 = round((row + 1) * self.height / grid_rows)
        
        if col == grid_cols - 1:
            x1 = self.width
        if row == grid_rows - 1:
            y1 = self.height
        
        n_sepal_len = self.normalize(data_row['sepal_length'], 
                                     stats['sepal_length']['min'], 
                                     stats['sepal_length']['max'])
        n_sepal_wid = self.normalize(data_row['sepal_width'], 
                                     stats['sepal_width']['min'], 
                                     stats['sepal_width']['max'])
        n_petal_len = self.normalize(data_row['petal_length'], 
                                     stats['petal_length']['min'], 
                                     stats['petal_length']['max'])
        n_petal_wid = self.normalize(data_row['petal_width'], 
                                     stats['petal_width']['min'], 
                                     stats['petal_width']['max'])
        
        palette = self.color_palettes.get(data_row['species'], [(128, 128, 128)] * 3)
        color_index = index % len(palette)
        base_color = palette[color_index]
        r, g, b = base_color
        
        r = self.clamp(r * (0.5 + n_sepal_len * 0.5))
        g = self.clamp(g * (0.5 + n_sepal_wid * 0.5))
        b = self.clamp(b * (0.5 + n_petal_len * 0.5))
        
        draw.rectangle([x0, y0, x1, y1], fill=(r, g, b))
    
    def generate(self, csv_path, output_path):
        """Génère une image à partir d'un fichier CSV"""
        df = pd.read_csv(csv_path)
        
        sort_cols = ['species', 'sepal_length', 'petal_length', 'petal_width']
        for c in sort_cols:
            if c not in df.columns:
                raise KeyError(f"Colonne manquante dans le CSV : '{c}'")
        
        df = df.sort_values(by=sort_cols, kind='mergesort').reset_index(drop=True)
        
        if len(df) == 0:
            raise ValueError("Le fichier CSV ne contient aucune ligne utilisable.")
        
        num_cells = len(df)
        grid_cols, grid_rows = self.calculate_optimal_grid(num_cells)
        
        print(f"📊 Dataset : {num_cells} lignes")
        print(f"🎨 Grille exacte : {grid_cols}x{grid_rows} = {grid_cols * grid_rows} cellules")
        
        stats = {
            'sepal_length': {'min': df['sepal_length'].min(), 'max': df['sepal_length'].max()},
            'sepal_width': {'min': df['sepal_width'].min(), 'max': df['sepal_width'].max()},
            'petal_length': {'min': df['petal_length'].min(), 'max': df['petal_length'].max()},
            'petal_width': {'min': df['petal_width'].min(), 'max': df['petal_width'].max()}
        }
        
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        for index in range(num_cells):
            row = df.iloc[index]
            self.draw_data_cell(draw, row, index, grid_cols, grid_rows, stats)
        
        img.save(output_path)
        print(f"✅ Image sauvegardée : {output_path}")
        
        return output_path
    
    def generate_from_dataframe(self, df, output_path):
        """Génère une image à partir d'un DataFrame"""
        sort_cols = ['species', 'sepal_length', 'petal_length', 'petal_width']
        for c in sort_cols:
            if c not in df.columns:
                raise KeyError(f"Colonne manquante dans le DataFrame : '{c}'")
        
        df = df.sort_values(by=sort_cols, kind='mergesort').reset_index(drop=True)
        
        if len(df) == 0:
            raise ValueError("Le DataFrame ne contient aucune ligne utilisable.")
        
        num_cells = len(df)
        grid_cols, grid_rows = self.calculate_optimal_grid(num_cells)
        
        print(f"📊 Dataset : {num_cells} lignes")
        print(f"🎨 Grille exacte : {grid_cols}x{grid_rows} = {grid_cols * grid_rows} cellules")
        
        stats = {
            'sepal_length': {'min': df['sepal_length'].min(), 'max': df['sepal_length'].max()},
            'sepal_width': {'min': df['sepal_width'].min(), 'max': df['sepal_width'].max()},
            'petal_length': {'min': df['petal_length'].min(), 'max': df['petal_length'].max()},
            'petal_width': {'min': df['petal_width'].min(), 'max': df['petal_width'].max()}
        }
        
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        for index in range(num_cells):
            row = df.iloc[index]
            self.draw_data_cell(draw, row, index, grid_cols, grid_rows, stats)
        
        img.save(output_path)
        print(f"✅ Image sauvegardée : {output_path}")
        
        return output_path