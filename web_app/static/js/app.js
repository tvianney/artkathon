// Gestion de l'application
let currentData = [];

// Éléments du DOM
const generateBtn = document.getElementById('generateBtn');
const downloadBtn = document.getElementById('downloadBtn');
const dataTableContainer = document.getElementById('dataTableContainer');
const imageContainer = document.getElementById('imageContainer');
const status = document.getElementById('status');

// Charger les données automatiquement au démarrage
window.addEventListener('DOMContentLoaded', async () => {
    await loadData();
});

// Fonction pour charger les données
async function loadData() {
    showStatus('loading', 'Chargement des données...');
    
    try {
        const response = await fetch('/api/load-data');
        const result = await response.json();
        
        if (result.success) {
            currentData = result.data;
            displayData(result.data, result.columns);
            generateBtn.disabled = false;
            showStatus('success', `${result.data.length} lignes chargées avec succès`);
        } else {
            showStatus('error', `Erreur: ${result.error}`);
        }
    } catch (error) {
        showStatus('error', `Erreur de chargement: ${error.message}`);
    }
}

// Générer l'art
generateBtn.addEventListener('click', async () => {
    showStatus('loading', 'Génération en cours...');
    generateBtn.disabled = true;
    
    const loadingSpinner = document.createElement('span');
    loadingSpinner.className = 'loading-spinner';
    const originalContent = generateBtn.innerHTML;
    generateBtn.innerHTML = '';
    generateBtn.appendChild(loadingSpinner);
    generateBtn.appendChild(document.createTextNode(' Génération...'));
    
    const updatedData = collectDataFromTable();
    
    try {
        const response = await fetch('/api/generate-art', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ data: updatedData })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayImage(result.image_url);
            showStatus('success', `${result.message}`);
            downloadBtn.style.display = 'block';
        } else {
            showStatus('error', `Erreur: ${result.error}`);
        }
    } catch (error) {
        showStatus('error', `Erreur de génération: ${error.message}`);
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = originalContent;
    }
});

// Télécharger l'image
downloadBtn.addEventListener('click', () => {
    window.location.href = '/api/download-image/generated_art.png';
    showStatus('success', 'Téléchargement en cours...');
});

// Afficher les données dans un tableau éditable
function displayData(data, columns) {
    const table = document.createElement('table');
    
    // En-tête
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Corps
    const tbody = document.createElement('tbody');
    data.forEach((row, rowIndex) => {
        const tr = document.createElement('tr');
        
        columns.forEach(col => {
            const td = document.createElement('td');
            const value = row[col];
            
            // Champs éditables
            if (typeof value === 'number') {
                const input = document.createElement('input');
                input.type = 'number';
                input.step = '0.1';
                input.value = value;
                input.dataset.row = rowIndex;
                input.dataset.col = col;
                td.appendChild(input);
            } else {
                const input = document.createElement('input');
                input.type = 'text';
                input.value = value;
                input.dataset.row = rowIndex;
                input.dataset.col = col;
                td.appendChild(input);
            }
            
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    
    dataTableContainer.innerHTML = '';
    dataTableContainer.appendChild(table);
}

// Collecter les données du tableau
function collectDataFromTable() {
    const inputs = dataTableContainer.querySelectorAll('input');
    const data = [];
    const rows = {};
    
    inputs.forEach(input => {
        const rowIndex = parseInt(input.dataset.row);
        const col = input.dataset.col;
        
        if (!rows[rowIndex]) {
            rows[rowIndex] = {};
        }
        
        const value = input.type === 'number' ? parseFloat(input.value) : input.value;
        rows[rowIndex][col] = value;
    });
    
    Object.keys(rows).forEach(key => {
        data.push(rows[key]);
    });
    
    return data;
}

// Afficher l'image générée
function displayImage(imageUrl) {
    imageContainer.innerHTML = `
        <img id="generatedImage" src="${imageUrl}?t=${Date.now()}" alt="Art généré">
    `;
}

// Afficher un message de statut
function showStatus(type, message) {
    status.className = `status ${type}`;
    status.textContent = message;
    
    if (type === 'success') {
        setTimeout(() => {
            status.style.display = 'none';
        }, 5000);
    }
}
