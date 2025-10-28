from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
from pathlib import Path
from art_engine import ArtGenerator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['OUTPUT_FOLDER']).mkdir(exist_ok=True)

DEFAULT_CSV = '../data/IRIS.csv'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/load-data', methods=['GET'])
def load_data():
    try:
        df = pd.read_csv(DEFAULT_CSV)
        data = df.to_dict('records')
        return jsonify({
            'success': True,
            'data': data,
            'columns': list(df.columns)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate-art', methods=['POST'])
def generate_art():
    try:
        data = request.json.get('data')
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        print(f"Génération avec {len(data)} lignes...")
        
        df = pd.DataFrame(data)
        temp_csv = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_data.csv')
        df.to_csv(temp_csv, index=False)
        
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'generated_art.png')
        generator = ArtGenerator()
        generator.generate(temp_csv, output_path)
        
        print("Art généré!")
        
        return jsonify({
            'success': True,
            'image_url': f'/api/get-image/generated_art.png',
            'message': f'Œuvre générée avec {len(df)} fleurs'
        })
    except Exception as e:
        import traceback
        print(f"Erreur: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/get-image/<filename>')
def get_image(filename):
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        return send_file(filepath, mimetype='image/png')
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

@app.route('/api/download-image/<filename>')
def download_image(filename):
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        return send_file(filepath, as_attachment=True, download_name='iris_art.png')
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

if __name__ == '__main__':
    print("Serveur IRIS sur http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

