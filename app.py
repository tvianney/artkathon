# app.py - The FINAL Backend Code 
from flask import Flask, render_template, request
import pandas as pd
from PIL import Image, ImageDraw
from colorsys import hls_to_rgb
import io
import base64
import numpy as np
import os
import random # For random position offset (Dispersion Logic)


app = Flask(__name__)
IMAGE_SIZE = 800
MAX_RADIUS = 40
DATA_FILE = 'IRIS.csv' 
CORRECT_COLS = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species']


def hls_to_rgba(hue, lightness, saturation, alpha_norm):
    """Converts HSL to RGBA tuple (FIXED to match call arguments)"""
    r, g, b = hls_to_rgb(hue / 360.0, lightness / 100.0, saturation / 100.0)
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    alpha = int(alpha_norm * 255)
    return (r, g, b, alpha)

def get_species_hue(species):
    """Maps the Species name to a specific HSL Hue value."""
    species = species.lower()
    if 'setosa' in species:
        return 30
    elif 'versicolor' in species:
        return 180
    elif 'virginica' in species:
        return 270
    else:
        return 0

# --- DATA LOADING ---

def load_initial_data():
    """Loads all data from IRIS.csv and prepares it as a list of lists."""
    if not os.path.exists(DATA_FILE):
        print(f"ERROR: {DATA_FILE} not found. Using small fallback data.")
        return [[5.1, 3.5, 1.4, 0.2, 'Iris-setosa'], [6.2, 3.4, 5.4, 2.3, 'Iris-virginica']]
        
    try:
        df = pd.read_csv(DATA_FILE, names=CORRECT_COLS, header=0)
        df.dropna(inplace=True) 
        df.drop_duplicates(inplace=True)
        
        data_list = df.values.tolist()
        final_list = []
        for row in data_list:
             final_list.append([float(x) for x in row[:4]] + [str(row[4])])
        
        print(f"SUCCESS: Loaded {len(final_list)} data points from {DATA_FILE}.")
        return final_list
        
    except Exception as e:
        print(f"CRITICAL ERROR loading data: {e}. Please check CSV headers: {CORRECT_COLS}")
        return [[5.1, 3.5, 1.4, 0.2, 'Iris-setosa'], [6.2, 3.4, 5.4, 2.3, 'Iris-virginica']]

# CORE ART GENERATION FUNCTION ---

def generate_art_from_list(data_list):
    """Generates the abstract image from the list of data points."""
    
    if not data_list:
        return None # Return None if list is empty
    
    df = pd.DataFrame(data_list, columns=CORRECT_COLS)
    
    # --- Normalization ---
    numeric_cols = CORRECT_COLS[:-1]
    for col in numeric_cols:
        min_val = df[col].min()
        max_val = df[col].max()
        range_val = max_val - min_val
        
        if range_val == 0:
            df[f'Norm_{col}'] = 0.5 
        else:
            df[f'Norm_{col}'] = (df[col] - min_val) / range_val
    
    # --- Generative Algorithm Setup ---
    img = Image.new('RGB', (IMAGE_SIZE, IMAGE_SIZE), (0, 0, 0)) # Black background
    draw = ImageDraw.Draw(img, 'RGBA') 
    
    for index, row in df.iterrows():
        # --- MAPPING & TRANSFORMATION ---
        
        #  POSITION (X & Y) - Only direct mapping (No random offset fix)
        # This mapping uses the full range of the canvas for the given data's range
        x = int(row['Norm_sepal_length'] * IMAGE_SIZE)
        y = int(row['Norm_sepal_width'] * IMAGE_SIZE)
        
        #  SIZE (Radius)
        radius = 5 + int(row['Norm_petal_length'] * MAX_RADIUS) 
        
        # COLOR (Hue) and OPACITY (Alpha)
        species_name = row['species'] 
        hue = get_species_hue(species_name)
        alpha_norm = row['Norm_petal_width']
        
        # Opacity Adjustment (Ensures minimum visibility is 50%)
        MIN_OPACITY_FACTOR = 0.5 # Increased visibility
        adjusted_alpha_norm = MIN_OPACITY_FACTOR + (alpha_norm * (1 - MIN_OPACITY_FACTOR))

        final_color = hls_to_rgba(
            hue=hue, 
            lightness=60, 
            saturation=90, 
            alpha_norm=adjusted_alpha_norm
        )
        
        # --- DRAWING LOGIC: Species determines the Form ---
        bbox = (x - radius, y - radius, x + radius, y + radius)
        
        if 'setosa' in species_name.lower():
            draw.ellipse(bbox, fill=final_color) # Circle
            
        elif 'versicolor' in species_name.lower():
            draw.rectangle(bbox, fill=final_color) # Square

        elif 'virginica' in species_name.lower():
            try:
                # Triangle Calculation
                h_offset = radius * np.sqrt(3) / 2
                v_offset = radius / 2
                triangle_coords = [(x, y - radius), (x - h_offset, y + v_offset), (x + h_offset, y + v_offset)]
                draw.polygon(triangle_coords, fill=final_color)
            except NameError:
                draw.ellipse(bbox, fill=final_color)
        else:
            draw.point((x, y), fill=final_color)

    # Convert the image to a Base64 string
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str

# FLASK ROUTES ---


FULL_IRIS_DATA = load_initial_data()

@app.route('/', methods=['GET', 'POST'])
def index():
    # Base data is always the full dataset
    base_data_list = FULL_IRIS_DATA 
    
    if request.method == 'POST':
        # When data is submitted from the form (for testing)
        try:
            input_text = request.form.get('data_input')
            lines = input_text.strip().split('\n')
            
            data_points = []
            for line in lines:
                if line.strip(): # Skip empty lines
                    parts = line.split(',')
                    data_points.append([float(p.strip()) if i < 4 else p.strip() for i, p in enumerate(parts)])
            
            # Use the submitted data points for generation
            current_data_list = data_points 
            
            if not current_data_list: # If user clears the box
                image_data = None
            else:
                image_data = generate_art_from_list(current_data_list)
            
        except Exception as e:
            # If input data is bad, regenerate the art using the full dataset
            current_data_list = base_data_list
            image_data = generate_art_from_list(current_data_list)
            data_to_show_in_textarea = "\n".join([", ".join(map(str, row)) for row in base_data_list])
            return render_template('index.html', error=f"Data Input Error. Displaying full set. Error: {e}", default_data=data_to_show_in_textarea, image_size=IMAGE_SIZE)
            
    else:
        # Initial GET request: Use the full dataset for the first view
        current_data_list = base_data_list
        image_data = generate_art_from_list(current_data_list)

    # The text area always displays the data that was *just used* to generate the image
    data_to_show_in_textarea = "\n".join([", ".join(map(str, row)) for row in current_data_list])
    
    return render_template('index.html', image_data=image_data, default_data=data_to_show_in_textarea, image_size=IMAGE_SIZE)

if __name__ == '__main__':
    app.run(debug=True)