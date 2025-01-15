from flask import Flask, jsonify, send_from_directory
import os
import nbformat
from flask_cors import CORS
from graphviz import Source
from sklearn.tree import export_graphviz
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

# Variables de ejemplo (asegúrate de definirlas correctamente en tu entorno)
# clf_tree_reduced: el modelo del árbol de decisión entrenado
# X_train_reduced: datos de entrenamiento reducidos
# y_train: etiquetas de entrenamiento

app = Flask(__name__, static_folder='static')

# Habilitar CORS para la aplicación completa
CORS(app)

# Directorios configurados
DOCUMENTS_FOLDER = 'documentos'
STATIC_FOLDER = 'static'
app.config['DOCUMENTS_FOLDER'] = DOCUMENTS_FOLDER

# Crear directorios si no existen
os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

# Rutas para gráficos
@app.route('/arbol', methods=['GET'])
def servir_arbol():
    try:
        dot_path = os.path.join(STATIC_FOLDER, "arbol_malware.dot")
        png_path = os.path.join(STATIC_FOLDER, "arbol_malware.png")
        
        export_graphviz(
            clf_tree_reduced,
            out_file=dot_path,
            feature_names=X_train_reduced.columns,
            class_names=["benign", "adware", "malware"],
            rounded=True,
            filled=True
        )
        graph = Source.from_file(dot_path)
        graph.render(png_path.replace('.png', ''), format="png", cleanup=True)

        return send_from_directory(app.static_folder, 'arbol_malware.png')
    except Exception as e:
        return jsonify({'mensaje': str(e)}), 500

@app.route('/decision_boundary', methods=['GET'])
def servir_decision_boundary():
    try:
        def plot_decision_boundary(clf, X, y, plot_training=True, resolution=1000):
            mins = X.min(axis=0) - 1
            maxs = X.max(axis=0) + 1
            x1, x2 = np.meshgrid(np.linspace(mins[0], maxs[0], resolution),
                                 np.linspace(mins[1], maxs[1], resolution))
            X_new = np.c_[x1.ravel(), x2.ravel()]
            y_pred = clf.predict(X_new).reshape(x1.shape)
            custom_cmap = ListedColormap(['#fafab0', '#9898ff', '#a0faa0'])
            plt.contourf(x1, x2, y_pred, alpha=0.3, cmap=custom_cmap)
            custom_cmap2 = ListedColormap(['#7d7d58', '#4c4c7f', '#507d50'])
            plt.contour(x1, x2, y_pred, cmap=custom_cmap2, alpha=0.8)
            if plot_training:
                plt.plot(X[:, 0][y == 0], X[:, 1][y == 0], "yo", label="normal")
                plt.plot(X[:, 0][y == 1], X[:, 1][y == 1], "bs", label="adware")
                plt.plot(X[:, 0][y == 2], X[:, 1][y == 2], "g^", label="malware")
                plt.axis([mins[0], maxs[0], mins[1], maxs[1]])
            plt.xlabel('min_flowpktl', fontsize=14)
            plt.ylabel('flow_fin', fontsize=14, rotation=90)

        plt.figure(figsize=(12, 6))
        plot_decision_boundary(clf_tree_reduced, X_train_reduced.values, y_train)
        boundary_path = os.path.join(STATIC_FOLDER, 'decision_boundary.png')
        plt.savefig(boundary_path)
        plt.close()

        return send_from_directory(app.static_folder, 'decision_boundary.png')
    except Exception as e:
        return jsonify({'mensaje': str(e)}), 500

# Rutas para documentos Jupyter
@app.route('/documentos', methods=['GET'])
def obtener_documentos():
    try:
        archivos = [f for f in os.listdir(DOCUMENTS_FOLDER) if f.endswith('.ipynb')]
        if not archivos:
            return jsonify({"mensaje": "No hay archivos .ipynb en el directorio."}), 404
        return jsonify(archivos), 200
    except FileNotFoundError:
        return jsonify({"mensaje": "No se encontró el directorio de documentos"}), 404

@app.route('/documentos/contenido/<nombre>', methods=['GET'])
def ver_contenido_documento(nombre):
    try:
        notebook_path = os.path.join(DOCUMENTS_FOLDER, nombre)
        if os.path.exists(notebook_path) and nombre.endswith('.ipynb'):
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook_content = nbformat.read(f, as_version=4)

            resultados = []
            for cell in notebook_content.cells:
                if cell.cell_type == 'code' and cell.outputs:
                    output = cell.outputs[-1]
                    if 'text' in output:
                        resultados.append({
                            'tipo': 'texto',
                            'contenido': output['text']
                        })
                    elif 'data' in output:
                        if 'image/png' in output['data']:
                            resultados.append({
                                'tipo': 'imagen',
                                'contenido': output['data']['image/png']
                            })
                        elif 'application/json' in output['data']:
                            resultados.append({
                                'tipo': 'json',
                                'contenido': output['data']['application/json']
                            })
                        elif 'text/html' in output['data']:
                            resultados.append({
                                'tipo': 'html',
                                'contenido': output['data']['text/html']
                            })
            return jsonify(resultados), 200
        else:
            return jsonify({'mensaje': 'Archivo no encontrado o formato incorrecto'}), 404
    except Exception as e:
        return jsonify({'mensaje': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
