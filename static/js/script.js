// Función que se ejecuta cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function () {
    fetchNotebooksList();
});

// Función para obtener la lista de notebooks desde la API
function fetchNotebooksList() {
    fetch('https://dep-2jl0.onrender.com/documentos')
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
    fetch(`https://dep-2jl0.onrender.com/documentos/contenido/${notebookName}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            const contentDiv = document.getElementById('content');
            contentDiv.innerHTML = ''; // Limpiar contenido previo

            if (data.length === 0) {
                contentDiv.textContent = 'El notebook está vacío.';
                return;
            }

            // Renderizar las celdas
            data.forEach(cell => {
                if (cell.tipo === 'código') {
                    const codeBlock = document.createElement('pre');
                    codeBlock.textContent = cell.contenido;
                    contentDiv.appendChild(codeBlock);

                    cell.salidas.forEach(salida => {
                        if (salida.tipo === 'texto') {
                            const textBlock = document.createElement('pre');
                            textBlock.textContent = salida.contenido;
                            contentDiv.appendChild(textBlock);
                        } else if (salida.tipo === 'imagen') {
                            const img = document.createElement('img');
                            img.src = `data:image/png;base64,${salida.contenido}`;
                            contentDiv.appendChild(img);
                        }
                    });
                } else if (cell.tipo === 'texto') {
                    const markdownBlock = document.createElement('div');
                    markdownBlock.textContent = cell.contenido;
                    contentDiv.appendChild(markdownBlock);
                }
            });
        })
        .catch(error => {
            console.error('Error al obtener el contenido del notebook:', error);
            const contentDiv = document.getElementById('content');
            contentDiv.textContent = 'Error al cargar el contenido del notebook.';
        });
}
