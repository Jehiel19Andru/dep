document.addEventListener('DOMContentLoaded', function () {
    fetchNotebooksList();
});

function fetchNotebooksList() {
    fetch('https://dep-2jl0.onrender.com/documentos')
        .then(response => response.json())
        .then(data => {
            const notebooksList = document.getElementById('notebooks-list');
            notebooksList.innerHTML = '';

            if (data.length === 0) {
                notebooksList.innerHTML = '<li>No se encontraron archivos .ipynb</li>';
                return;
            }

            data.forEach(notebook => {
                const li = document.createElement('li');
                li.textContent = notebook;
                li.onclick = () => fetchNotebookContent(notebook);
                notebooksList.appendChild(li);
            });
        })
        .catch(error => console.error('Error al obtener la lista de notebooks:', error));
}

function fetchNotebookContent(notebookName) {
    fetch(`https://dep-2jl0.onrender.com/documentos/contenido/${notebookName}`)
        .then(response => response.json())
        .then(outputs => {
            const contentDiv = document.getElementById('content');
            contentDiv.innerHTML = '';

            outputs.forEach(output => {
                if (output.tipo === 'texto') {
                    const textOutput = document.createElement('pre');
                    textOutput.textContent = output.contenido;
                    contentDiv.appendChild(textOutput);
                } else if (output.tipo === 'imagen') {
                    const img = document.createElement('img');
                    img.src = `data:image/png;base64,${output.contenido}`;
                    contentDiv.appendChild(img);
                } else if (output.tipo === 'html') {
                    const htmlOutput = document.createElement('div');
                    htmlOutput.innerHTML = output.contenido;
                    contentDiv.appendChild(htmlOutput);
                } else if (output.tipo === 'json') {
                    const jsonOutput = document.createElement('pre');
                    jsonOutput.textContent = JSON.stringify(output.contenido, null, 2);
                    contentDiv.appendChild(jsonOutput);
                }
            });
        })
        .catch(error => console.error('Error al obtener el contenido del notebook:', error));
}
