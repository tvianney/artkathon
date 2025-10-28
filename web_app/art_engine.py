import pandas as pd
from PIL import Image, ImageDraw
import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config.settings import *

class ArtGenerator:
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width = width
        self.height = height
        self.background_color = BACKGROUND_COLOR
        
        self.color_palettes = COLOR_PALETTES
    
    def normalize(self, value, min_val, max_val, new_min, new_max):
        if max_val == min_val:
            return (new_max + new_min) / 2
        return ((value - min_val) / (max_val - min_val)) * (new_max - new_min) + new_min
    
    def get_color_from_data(self, species, sepal_length, petal_length, stats):
        palette = self.color_palettes.get(species, [(255, 255, 255)])
        
        ratio = sepal_length / (petal_length + 0.1)
        ratio_normalized = self.normalize(ratio, 0.5, 3.0, 0, len(palette) - 1)
        index = int(ratio_normalized)
        
        index = max(0, min(index, len(palette) - 1))
        
        return palette[index]
    
    def calculate_shape_params(self, row, stats):
        margin = SHAPE_MARGIN
        
        x = self.normalize(
            row['sepal_length'], 
            stats['sepal_length']['min'], 
            stats['sepal_length']['max'], 
            margin, 
            self.width - margin
        )
        
        y = self.normalize(
            row['sepal_width'], 
            stats['sepal_width']['min'], 
            stats['sepal_width']['max'], 
            margin, 
            self.height - margin
        )
        
        size = self.normalize(
            row['petal_length'], 
            stats['petal_length']['min'], 
            stats['petal_length']['max'], 
            SIZE_MIN,
            SIZE_MAX
        )
        
        num_sides = int(self.normalize(
            row['petal_width'], 
            stats['petal_width']['min'], 
            stats['petal_width']['max'], 
            SIDES_MIN,
            SIDES_MAX
        ))
        
        ratio = row['sepal_length'] / (row['petal_length'] + 0.1)
        rotation = self.normalize(ratio, 0.5, 3.0, 0, 360)
        
        color = self.get_color_from_data(
            row['species'], 
            row['sepal_length'], 
            row['petal_length'], 
            stats
        )
        
        opacity = int(self.normalize(
            row['petal_width'], 
            stats['petal_width']['min'], 
            stats['petal_width']['max'], 
            OPACITY_MIN,
            OPACITY_MAX
        ))
        
        return {
            'x': x,
            'y': y,
            'size': size,
            'num_sides': num_sides,
            'rotation': rotation,
            'color': color,
            'opacity': opacity
        }
    
    def draw_background_gradient(self, draw, df, stats):
        num_bands = 5
        quantiles = [df['sepal_width'].quantile(i / num_bands) for i in range(num_bands + 1)]
        
        for i in range(num_bands):
            y_start = int((i / num_bands) * self.height)
            y_end = int(((i + 1) / num_bands) * self.height)
            
            band_data = df[
                (df['sepal_width'] >= quantiles[i]) & 
                (df['sepal_width'] < quantiles[i + 1])
            ]
            
            if len(band_data) == 0:
                continue
            
            species_counts = band_data['species'].value_counts()
            dominant_species = species_counts.idxmax() if len(species_counts) > 0 else 'Iris-setosa'
            
            palette = self.color_palettes.get(dominant_species, [(50, 50, 70)])
            
            mixed_color = [0, 0, 0]
            total_count = len(band_data)
            
            for species in species_counts.index:
                weight = species_counts[species] / total_count
                species_palette = self.color_palettes.get(species, [(50, 50, 70)])
                base_color = species_palette[0]
                
                for c in range(3):
                    mixed_color[c] += base_color[c] * weight
            
            mixed_color = tuple(int(c) for c in mixed_color)
            
            num_segments = 8
            petal_quantiles = [band_data['petal_length'].quantile(i / num_segments) for i in range(num_segments + 1)]
            
            for j in range(num_segments):
                x_start = int((j / num_segments) * self.width)
                x_end = int(((j + 1) / num_segments) * self.width)
                
                segment_data = band_data[
                    (band_data['petal_length'] >= petal_quantiles[j]) & 
                    (band_data['petal_length'] < petal_quantiles[j + 1])
                ]
                
                if len(segment_data) > 0:
                    intensity = self.normalize(
                        len(segment_data),
                        0,
                        len(band_data) / num_segments * 2,
                        0.3,
                        0.7
                    )
                else:
                    intensity = 0.4
                
                segment_color = tuple(int(c * intensity) for c in mixed_color)
                
                draw.rectangle(
                    [x_start, y_start, x_end, y_end],
                    fill=segment_color + (180,)
                )
        
        # halos d'espèces
        for species_name in df['species'].unique():
            species_data = df[df['species'] == species_name]
            
            centroid_x = self.normalize(
                species_data['sepal_length'].mean(),
                stats['sepal_length']['min'],
                stats['sepal_length']['max'],
                0,
                self.width
            )
            
            centroid_y = self.normalize(
                species_data['sepal_width'].mean(),
                stats['sepal_width']['min'],
                stats['sepal_width']['max'],
                0,
                self.height
            )
            
            spread = self.normalize(
                species_data['petal_length'].std(),
                0,
                2,
                200,
                500
            )
            
            palette = self.color_palettes.get(species_name, [(100, 100, 100)])
            color = palette[1]
            
            for k in range(3):
                current_size = spread * (1 + k * 0.3)
                alpha = 30 - k * 8
                
                bbox = [
                    centroid_x - current_size/2,
                    centroid_y - current_size/2,
                    centroid_x + current_size/2,
                    centroid_y + current_size/2
                ]
                draw.ellipse(bbox, fill=color + (alpha,))
    
    def draw_flower(self, draw, row, stats):
        params = self.calculate_shape_params(row, stats)
        
        points = []
        for i in range(params['num_sides']):
            angle = math.radians((360 / params['num_sides']) * i + params['rotation'])
            px = params['x'] + params['size'] * math.cos(angle)
            py = params['y'] + params['size'] * math.sin(angle)
            points.append((px, py))
        
        color_with_alpha = params['color'] + (params['opacity'],)
        
        halo_size = params['size'] * 1.3
        halo_points = []
        for i in range(params['num_sides']):
            angle = math.radians((360 / params['num_sides']) * i + params['rotation'])
            px = params['x'] + halo_size * math.cos(angle)
            py = params['y'] + halo_size * math.sin(angle)
            halo_points.append((px, py))
        
        halo_alpha = int(params['opacity'] * 0.3)
        draw.polygon(halo_points, fill=params['color'] + (halo_alpha,), outline=None)
        
        draw.polygon(
            points, 
            fill=color_with_alpha, 
            outline=params['color'] + (255,), 
            width=3
        )
        
        center_size = params['size'] * 0.2
        center_box = [
            params['x'] - center_size,
            params['y'] - center_size,
            params['x'] + center_size,
            params['y'] + center_size
        ]
        center_color = tuple(min(255, c + 50) for c in params['color'])
        draw.ellipse(center_box, fill=center_color + (255,))
    
    def generate(self, csv_path, output_path):
        df = pd.read_csv(csv_path)
        
        stats = {
            'sepal_length': {
                'min': df['sepal_length'].min(), 
                'max': df['sepal_length'].max()
            },
            'sepal_width': {
                'min': df['sepal_width'].min(), 
                'max': df['sepal_width'].max()
            },
            'petal_length': {
                'min': df['petal_length'].min(), 
                'max': df['petal_length'].max()
            },
            'petal_width': {
                'min': df['petal_width'].min(), 
                'max': df['petal_width'].max()
            }
        }
        
        img = Image.new('RGBA', (self.width, self.height), self.background_color + (255,))
        draw = ImageDraw.Draw(img, 'RGBA')
        
        self.draw_background_gradient(draw, df, stats)
        
        for index, row in df.iterrows():
            self.draw_flower(draw, row, stats)
        
        final_img = Image.new('RGB', img.size, self.background_color)
        final_img.paste(img, mask=img.split()[3])
        
        final_img.save(output_path, 'PNG')
        
        return output_path
    
    def generate_from_dataframe(self, df, output_path):
        stats = {
            'sepal_length': {
                'min': df['sepal_length'].min(), 
                'max': df['sepal_length'].max()
            },
            'sepal_width': {
                'min': df['sepal_width'].min(), 
                'max': df['sepal_width'].max()
            },
            'petal_length': {
                'min': df['petal_length'].min(), 
                'max': df['petal_length'].max()
            },
            'petal_width': {
                'min': df['petal_width'].min(), 
                'max': df['petal_width'].max()
            }
        }
        
        img = Image.new('RGBA', (self.width, self.height), self.background_color + (255,))
        draw = ImageDraw.Draw(img, 'RGBA')
        
        self.draw_background_gradient(draw, df, stats)
        
        for index, row in df.iterrows():
            self.draw_flower(draw, row, stats)
        
        final_img = Image.new('RGB', img.size, self.background_color)
        final_img.paste(img, mask=img.split()[3])
        
        final_img.save(output_path, 'PNG')
        
        return output_path
