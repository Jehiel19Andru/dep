// Función que se ejecuta cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function () {
    fetchNotebooksList();
});

// Función para obtener la lista de notebooks desde la API
function fetchNotebooksList() {
    fetch('/documentos')
        .then(response => response.json())
        .then(data => {
            const notebooksList = document.getElementById('notebooks-list');
            notebooksList.innerHTML = ''; // Limpiar la lista antes de agregar los items

            if (data.length === 0) {
                notebooksList.innerHTML = '<li>No se encontraron archivos .ipynb</li>';
                return;
            }

            // Agregar cada archivo a la lista como un enlace
            data.forEach(notebook => {
                const li = document.createElement('li');
                li.textContent = notebook;
                li.style.cursor = 'pointer'; // Cambiar el cursor para indicar que es clicable
                li.onclick = () => fetchNotebookContent(notebook); // Abrir el contenido al hacer clic
                notebooksList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error al obtener la lista de notebooks:', error);
        });
}

// Función para obtener el contenido de un notebook
function fetchNotebookContent(notebookName) {
    fetch(`/documentos/contenido/${notebookName}`)
        .then(response => response.json())
        .then(data => {
            const contentDiv = document.getElementById('content');
            contentDiv.innerHTML = ''; // Limpiar contenido previo

            // Iterar sobre las celdas del notebook
            data.forEach(cell => {
                if (cell.tipo === 'código') {
                    cell.salidas.forEach(salida => {
                        // Renderizar imágenes
                        if (salida.tipo === 'imagen') {
                            const imgElement = document.createElement('img');
                            imgElement.src = `data:image/png;base64,${salida.contenido}`;
                            imgElement.alt = 'Imagen de salida';
                            contentDiv.appendChild(imgElement);
                        }

                        // Renderizar texto
                        if (salida.tipo === 'texto') {
                          const textElement = document.createElement('pre');
                            textElement.textContent = salida.contenido; // Asignar el texto
                            textElement.style.padding = '15px';
                            textElement.style.border = '1px solid #ccc';
                            textElement.style.borderRadius = '8px';
                            textElement.style.backgroundColor = '#f9f9f9';
                            textElement.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
                            textElement.style.margin = '15px 0';
                            textElement.style.fontFamily = '"Courier New", Courier, monospace';
                            textElement.style.fontSize = '14px';
                            textElement.style.color = '#333';
                            textElement.style.whiteSpace = 'pre-wrap'; // Para manejar texto largo con saltos de línea
                            textElement.style.wordWrap = 'break-word';
                        contentDiv.appendChild(textElement);
                        }
                    });
                }
            });
        })
        .catch(error => {
            console.error('Error al obtener el contenido del notebook:', error);
        });
}
