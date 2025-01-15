from flask import Flask, jsonify, request, send_from_directory
import os
import nbformat
from graphviz import Source
from sklearn.tree import export_graphviz

# Configuración
DOCUMENTS_FOLDER = 'documentos'
STATIC_FOLDER = 'static'
DOT_FILE = os.path.join(DOCUMENTS_FOLDER, 'android_malware.dot')
PNG_FILE = os.path.join(DOCUMENTS_FOLDER, 'android_malware.png')

# Crear la aplicación Flask
app = Flask(__name__, static_folder=STATIC_FOLDER)
app.config['DOCUMENTS_FOLDER'] = DOCUMENTS_FOLDER

# Verificar o crear el directorio de documentos
if not os.path.exists(DOCUMENTS_FOLDER):
    os.makedirs(DOCUMENTS_FOLDER)

@app.route('/')
def home():
    """Devuelve el archivo index.html desde el directorio estático."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/documentos', methods=['GET'])
def obtener_documentos():
    """Lista los archivos .ipynb disponibles en el directorio de documentos."""
    try:
        archivos = [f for f in os.listdir(app.config['DOCUMENTS_FOLDER']) if f.endswith('.ipynb')]

        if not archivos:
            return jsonify({"mensaje": "No hay archivos .ipynb en el directorio."}), 404

        return jsonify(archivos), 200
    except Exception as e:
        return jsonify({"mensaje": f"Error al listar los documentos: {str(e)}"}), 500
        
@app.route('/documentos/contenido/<nombre>', methods=['GET'])
def ver_contenido_documento(nombre):
    """Devuelve el contenido de un archivo .ipynb en formato JSON."""
    try:
        notebook_path = os.path.join(app.config['DOCUMENTS_FOLDER'], nombre)

        if not os.path.exists(notebook_path):
            return jsonify({'mensaje': 'Archivo no encontrado'}), 404

        if not nombre.endswith('.ipynb'):
            return jsonify({'mensaje': 'El archivo no tiene formato .ipynb'}), 400

        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = nbformat.read(f, as_version=4)

        contenido = []
        for cell in notebook_content.cells:
            if cell.cell_type == 'code':
                cell_data = {
                    'tipo': 'código',
                    'contenido': cell.source,
                    'salidas': []
                }

                for output in cell.outputs:
                    if 'text' in output:
                        cell_data['salidas'].append({'tipo': 'texto', 'contenido': output['text']})
                    elif 'data' in output:
                        if 'image/png' in output['data']:
                            cell_data['salidas'].append({'tipo': 'imagen', 'contenido': output['data']['image/png']})
                
                contenido.append(cell_data)
            elif cell.cell_type == 'markdown':
                contenido.append({'tipo': 'texto', 'contenido': cell.source})

        return jsonify(contenido), 200
    except Exception as e:
        return jsonify({'mensaje': f"Error al procesar el archivo: {str(e)}"}), 500

@app.route('/generar-arbol', methods=['POST'])
def generar_arbol():
    """Genera un archivo .dot y una imagen .png a partir de un árbol de decisión."""
    try:
        # Parámetros simulados
        feature_names = ['feature1', 'feature2']  # Sustituir con tus columnas reales
        class_names = ['benign', 'adware', 'malware']

        # Generar archivo .dot
        export_graphviz(
            clf=None,  # Sustituir con tu modelo entrenado
            out_file=DOT_FILE,
            feature_names=feature_names,
            class_names=class_names,
            rounded=True,
            filled=True
        )

        # Convertir .dot a .png
        source = Source.from_file(DOT_FILE)
        source.render(PNG_FILE, format='png', cleanup=False)

        return jsonify({"mensaje": "Árbol generado correctamente.", "imagen": "android_malware.png"}), 200
    except Exception as e:
        return jsonify({"mensaje": f"Error al generar el árbol: {str(e)}"}), 500

@app.route('/documentos/imagen/<nombre>', methods=['GET'])
def servir_imagen(nombre):
    """Devuelve una imagen almacenada en el directorio de documentos."""
    try:
        imagen_path = os.path.join(app.config['DOCUMENTS_FOLDER'], nombre)
        if os.path.exists(imagen_path):
            return send_from_directory(app.config['DOCUMENTS_FOLDER'], nombre)
        else:
            return jsonify({"mensaje": "Imagen no encontrada."}), 404
    except Exception as e:
        return jsonify({"mensaje": f"Error al servir la imagen: {str(e)}"}), 500

# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
