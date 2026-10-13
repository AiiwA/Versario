/**
 * Versario - Lógica de JavaScript para la aplicación frontend
 * 
 * Funcionalidades:
 * - Gestión de lista de poemas
 * - Creación de nuevos poemas
 * - Generación asíncrona de audio con polling
 * - Reproductor de audio integrado
 * - Descarga de archivos MP3
 */

// ==============================
// Configuración global
// ==============================

const API_BASE = '/api';
const POLLING_INTERVAL = 2000; // 2 segundos para verificar estado
const AUDIO_PATH_REGEX = /^https?:\/\//i; // Detectar si es URL externa

let currentPage = 1;
let totalPages = 1;
let isLoadingPoems = false;

// ==============================
// Inicialización
// ==============================

document.addEventListener('DOMContentLoaded', () => {
    initForm();
    loadPoems();
    
    // Cargar voces disponibles en selector
    if (typeof loadVoices === 'function') {
        loadVoices();
    }
});

// ==============================
// Gestión de formularios y creación
// ==============================

function initForm() {
    const form = document.getElementById('poemForm');
    
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const poemaData = {
            titulo: formData.get('titulo'),
            autor: formData.get('autor') || null,
            texto: formData.get('texto'),
            voz: formData.get('voz'),
            velocidad: parseFloat(formData.get('velocidad'))
        };
        
        // Validaciones finales
        if (!poemaData.titulo.trim()) {
            showError('El título del poema es obligatorio');
            return;
        }
        
        if (poemaData.texto.length > 10000) {
            showError('El texto no puede exceder 10,000 caracteres');
            return;
        }
        
        if (!poemaData.voz || poemaData.voz === '') {
            showError('Por favor selecciona una voz TTS');
            return;
        }
        
        if (isNaN(poemaData.velocidad) || poemaData.velocidad < 0.8 || poemaData.velocidad > 1.2) {
            showError('La velocidad debe estar entre 0.8x y 1.2x');
            return;
        }
        
        await createPoema(poemaData);
    });
}

async function createPoema(poemaData) {
    try {
        // Deshabilitar formulario mientras se envía
        const submitBtn = document.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span> Enviando...';
        
        const response = await fetch(`${API_BASE}/poemas/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(poemaData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al crear el poema');
        }
        
        // Redirigir a la página de detalle del nuevo poema
        const data = await response.json();
        navigateToPoemaDetail(data.id);
        
    } catch (error) {
        console.error('Error creando poema:', error);
        showError(error.message || 'Ocurrió un error. Intenta de nuevo.');
    } finally {
        // Reestablecer botón
        const submitBtn = document.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '📤 Subir poema y generar audio';
        }
    }
}

// ==============================
// Listado de poemas
// ==============================

async function loadPoems() {
    const container = document.getElementById('poemsContainer');
    
    if (!container) return;
    
    if (isLoadingPoems) return; // Evitar múltiples llamadas
    
    try {
        isLoadingPoems = true;
        
        const response = await fetch(`${API_BASE}/poemas/?offset=0&limit=${totalPages}`);
        
        if (!response.ok) {
            throw new Error('Error al cargar poemas');
        }
        
        const poems = await response.json();
        totalPages = Math.ceil((currentPage * 1000) / 1000 + 2); // Calculo simplificado
        
        renderPoems(poems);
        
        if (poems.length === 0) {
            document.getElementById('emptyState').classList.remove('hidden');
            container.innerHTML = '';
        } else {
            document.getElementById('emptyState').classList.add('hidden');
        }
        
    } catch (error) {
        console.error('Error cargando poemas:', error);
        showError(error.message || 'No se pudieron cargar los poemas');
    } finally {
        isLoadingPoems = false;
    }
}

function renderPoems(poems) {
    const container = document.getElementById('poemsContainer');
    const emptyState = document.getElementById('emptyState');
    
    if (!container) return;
    
    container.innerHTML = poems.map(poema => createPoemaCard(poema)).join('');
}

function createPoemaCard(poema) {
    // Determinar mensaje según estado
    let statusHtml = '';
    if (poema.estado === 'generando') {
        statusHtml = `<div class="status-badge generando">
            <span class="status-icon">⏳</span>
            <span class="status-text">Generando...</span>
          </div>`;
    } else if (poema.estado === 'pendiente') {
        statusHtml = `<div class="status-badge pendiente">
            <span class="status-icon">📋</span>
            <span class="status-text">Pendiente</span>
          </div>`;
    } else if (poema.estado === 'error') {
        statusHtml = `<div class="status-badge error">
            <span class="status-icon">⚠️</span>
            <span class="status-text">Error</span>
          </div>`;
    }
    
    const audioButton = poema.ruta_audio 
        ? `<button class="btn btn-play" onclick="playAudio('${poema.id}')">
             <span class="icon">▶️</span>
             <span class="label">Reproducir</span>
            </button>`
        : `<span style="color: var(--color-text-muted); font-size: 0.9rem;">⏳ Audio pendiente...</span>`;
    
    const downloadButton = poema.ruta_audio 
        ? `<a href="/api/poemas/${poema.id}/audio" class="btn btn-download" download>
             📥 Descargar
            </a>`
        : '';
    
    return `
      <article class="poema-card">
        ${statusHtml}
        
        <div class="card-header">
          <h3>${escapeHtml(poema.titulo)}</h3>
          ${poema.autor ? `<p class="card-subtitle">— ${escapeHtml(poema.autor)}</p>` : ''}
        </div>
        
        <!-- Vista previa del texto (primeros 500 caracteres) -->
        <div class="poema-preview">
          <p>${escapeHtml(truncateText(poema.texto, 200))}</p>
        </div>
        
        <div class="card-footer">
          ${audioButton}
          
          <div class="card-actions">
            ${downloadButton}
            
            <button class="btn btn-secondary" onclick="viewPoemaDetail('${poema.id}')" style="margin-left: 8px;">
              👁️ Ver detalle
            </button>
            
            <button class="btn btn-secondary" onclick="deletePoema(${poema.id})" style="margin-left: 8px; color: var(--color-error);">
              🗑️ Borrar
            </button>
          </div>
        </div>
        
        <!-- Progress bar para estado generando -->
        ${poema.estado === 'generando' ? `
          <div class="progress-container mt-md">
            <div class="progress-bar" style="background: var(--color-warning);">
              <div class="progress-fill" id="progress-${poema.id}" style="width: 30%;"></div>
            </div>
          </div>
        ` : ''}
      </article>
    `;
}

// ==============================
// Detalles del poema y reproductor
// ==============================

async function viewPoemaDetail(poemaId) {
    try {
        const response = await fetch(`${API_BASE}/poemas/${poemaId}`);
        
        if (!response.ok) {
            throw new Error('Poema no encontrado');
        }
        
        const poema = await response.json();
        
        // Renderizar página de detalle (se reemplaza dinámicamente en el template)
        renderPoemaDetail(poema);
        
    } catch (error) {
        console.error('Error cargando detalle:', error);
        showError(error.message || 'No se pudo cargar el poema');
    }
}

function renderPoemaDetail(poema) {
    // Ocultar formulario y mostrar lista
    document.getElementById('createForm').classList.add('hidden');
    document.getElementById('poemsList').classList.remove('hidden');
    
    // Mostrar estado de generación
    const statusBadge = document.getElementById('generationStatus');
    if (statusBadge) {
        let estadoText = poema.estado;
        
        if (poema.estado === 'generando') {
            estadoText += '...';
            
            // Iniciar polling para verificar progreso
            startPolling(poema.id, () => checkPoemaStatus(poema.id), POLLING_INTERVAL);
        } else if (poema.estado === 'pendiente') {
            statusBadge.classList.add('hidden');
        } else if (poema.estado === 'error') {
            statusBadge.className = 'status-badge error';
        } else if (poema.estado === 'listo') {
            startPolling(poema.id, () => checkPoemaStatus(poema.id), POLLING_INTERVAL);
        }
        
        statusBadge.innerHTML = `
          <span class="status-icon">${getIconByState(poema.estado)}</span>
          <span class="status-text">${estadoText}</span>
        `;
    }
    
    // Actualizar texto del poema con tipografía editorial
    const poemTextElement = document.getElementById('poemText');
    if (poemTextElement) {
        poemTextElement.textContent = poema.texto || 'El poema no tiene contenido.';
        
        // Agregar estilo visual de estrofas si hay saltos de línea
        if (poema.texto.includes('\n')) {
            const paragraphs = poema.texto.split('\n\n');
            let formattedHtml = '<div style="text-align: justify;">';
            paragraphs.forEach(para => {
                if (para.trim()) {
                    formattedHtml += `<p>${escapeHtml(truncateText(para, 100))}</p>`;
                }
            });
            formattedHtml += '</div>';
            poemTextElement.innerHTML = formattedHtml;
        }
    }
    
    // Actualizar controles del reproductor
    const playBtn = document.getElementById('playBtn');
    if (playBtn) {
        playBtn.querySelector('.label').textContent = poema.ruta_audio 
            ? 'Reproducir' 
            : 'Generando audio...';
        
        if (!poema.ruta_audio) {
            playBtn.disabled = true;
            playBtn.classList.add('disabled');
        }
    }
    
    // Actualizar botón de descarga
    const downloadBtn = document.getElementById('downloadBtn');
    const noAudioMessage = document.getElementById('noAudioMessage');
    
    if (downloadBtn && !poema.ruta_audio) {
        downloadBtn.style.display = 'none';
        noAudioMessage.style.display = 'block';
    } else if (downloadBtn && poema.ruta_audio) {
        downloadBtn.style.display = 'block';
        noAudioMessage.style.display = 'none';
        
        // Iniciar polling para esperar audio generado
        startPolling(poema.id, () => checkPoemaStatus(poema.id), POLLING_INTERVAL);
    }
    
    // Actualizar información en el DOM (velocidad usada)
    const velocityDisplay = document.getElementById('velocityValue');
    if (velocityDisplay) {
        velocityDisplay.textContent = `${poema.velocidad}x`;
    }
    
    // Cargar voces disponibles si no está cargado
    if (!window.voicesLoaded) {
        loadVoices();
        window.voicesLoaded = true;
    }
}

function getIconByState(estado) {
    const icons = {
        'pendiente': '📋',
        'generando': '⏳',
        'listo': '✅',
        'error': '⚠️'
    };
    return icons[estado] || '';
}

function checkPoemaStatus(poemaId) {
    // Verificar periodicamente si el audio ya está listo
    const playBtn = document.getElementById('playBtn');
    
    if (!playBtn) return;
    
    fetch(`${API_BASE}/poemas/${poemaId}`)
        .then(response => response.json())
        .then(poema => {
            const wasGenerating = poema.estado === 'generando';
            
            // Actualizar estado visual
            updateAudioControls(poema.ruta_audio, poema.estado);
            
            // Si estaba generando y ahora está listo, limpiar polling
            if (wasGenerating && poema.estado !== 'generando') {
                stopPolling();
            }
        })
        .catch(error => {
            console.error('Error verificando estado:', error);
            showError('No se pudo verificar el estado del audio');
        });
}

function updateAudioControls(hasAudio, estado) {
    const playBtn = document.getElementById('playBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    
    if (hasAudio && !playBtn.disabled) {
        playBtn.classList.remove('disabled');
        playBtn.querySelector('.label').textContent = 'Reproducir';
    }
    
    if (estado === 'listo' || hasAudio) {
        downloadBtn.style.display = 'block';
    }
}

// ==============================
// Reproductor de audio
// ==============================

function playAudio(poemaId) {
    const audioPlayer = document.getElementById('audioPlayer');
    
    if (!audioPlayer) {
        alert('Reproductor no disponible en esta vista');
        return;
    }
    
    // Cargar audio si aún no está disponible
    fetch(`${API_BASE}/poemas/${poemaId}/audio`)
        .then(response => {
            if (response.status === 404) {
                alert('El audio aún se está generando. Por favor espera un momento.');
                return;
            }
            
            // Actualizar source y reproducir
            audioPlayer.src = response.url;
            audioPlayer.play();
        })
        .catch(error => {
            console.error('Error reproduciendo:', error);
            showError('No se pudo cargar el audio');
        });
}

// Control del reproductor
const playBtn = document.getElementById('playBtn');
const audioPlayer = document.getElementById('audioPlayer');
const volumeSlider = document.getElementById('volumeSlider');
const volumeValue = document.getElementById('volumeValue');
const muteBtn = document.getElementById('muteBtn');

if (playBtn && audioPlayer) {
    playBtn.addEventListener('click', () => {
        if (audioPlayer.paused) {
            // Verificar si el audio está cargado
            if (!audioPlayer.src || !AUDIO_PATH_REGEX.test(audioPlayer.src)) {
                alert('El audio aún no ha sido generado. Por favor espera un momento.');
                return;
            }
            
            audioPlayer.play();
        } else {
            audioPlayer.pause();
        }
    });
    
    // Control de volumen
    if (volumeSlider) {
        volumeSlider.addEventListener('input', () => {
            const value = volumeSlider.value;
            audioPlayer.volume = value / 100;
            volumeValue.textContent = `${value}%`;
            
            muteBtn.innerHTML = value > 0 ? '🔊' : '🔇';
        });
    }
    
    // Botón mute/sound
    if (muteBtn) {
        muteBtn.addEventListener('click', () => {
            const isMuted = volumeSlider.value === '0' || volumeSlider.value === 0;
            
            if (!isMuted) {
                volumeSlider.value = 0;
                volumeValue.textContent = '0%';
            } else {
                volumeSlider.value = 100;
                volumeValue.textContent = '100%';
            }
        });
    }
}

// ==============================
// Utilidades de UI
// ==============================

function showError(message) {
    const modal = document.getElementById('errorModal');
    const messageEl = document.getElementById('errorMessage');
    
    if (modal && messageEl) {
        messageEl.textContent = message;
        modal.classList.remove('hidden');
        
        // Ocultar después de 5 segundos si el usuario no interactúa
        setTimeout(() => {
            closeError();
        }, 10000);
    }
}

function closeError() {
    const modal = document.getElementById('errorModal');
    
    if (modal) {
        modal.classList.add('hidden');
    }
}

function showSuccess(message) {
    const modal = document.getElementById('successModal');
    const messageEl = document.getElementById('successMessage');
    
    if (modal && messageEl) {
        messageEl.textContent = message;
        modal.classList.remove('hidden');
        
        setTimeout(() => {
            closeSuccess();
        }, 3000);
    }
}

function closeSuccess() {
    const modal = document.getElementById('successModal');
    
    if (modal) {
        modal.classList.add('hidden');
    }
}

// ==============================
// Utilidades de texto
// ==============================

function truncateText(text, maxLength) {
    if (!text || text.length <= maxLength) {
        return text;
    }
    return text.substring(0, maxLength).trim() + '...';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==============================
// Carga de voces disponibles (simulada)
// ==============================

async function loadVoices() {
    // Intentar cargar voces del servidor
    try {
        const response = await fetch(`${API_BASE}/poemas/voices`);
        
        if (response.ok) {
            const voices = await response.json();
            
            const voiceSelect = document.getElementById('voz');
            if (voiceSelect && voices.length > 0) {
                voices.forEach(voice => {
                    const option = document.createElement('option');
                    option.value = voice.name;
                    option.textContent = `${voice.name} (${voice.gender || 'neutro'}) - ${voice.description || ''}`;
                    voiceSelect.appendChild(option);
                });
            }
        } else {
            // Fallback a voces predeterminadas si falla la API
            const defaultVoices = [
                { name: "es_ES_bahnc", gender: "female" },
                { name: "es_ES_damek", gender: "male" },
                { name: "es_LA_lunfardo", gender: "neutral" }
            ];
            
            const voiceSelect = document.getElementById('voz');
            if (voiceSelect && voices.length > 0) {
                defaultVoices.forEach(voice => {
                    const option = document.createElement('option');
                    option.value = voice.name;
                    option.textContent = `${voice.name} (${voice.gender || 'neutro'})`;
                    voiceSelect.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Error cargando voces:', error);
    }
}

// ==============================
// Funciones para navegación y borrado
// ==============================

function navigateToPoemaDetail(poemaId) {
    // Ocultar formulario de creación
    document.getElementById('createForm').classList.add('hidden');
    document.getElementById('poemsList').classList.remove('hidden');
    
    // Cargar detalle del poema
    viewPoemaDetail(poemaId);
}

async function deletePoema(poemaId) {
    if (!confirm('¿Estás seguro de que deseas borrar este poema y su audio? Esta acción no se puede deshacer.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/poemas/${poemaId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Error al borrar el poema');
        }
        
        // Eliminar la tarjeta del DOM
        const card = document.querySelector(`button[onclick="viewPoemaDetail('${poemaId}')"]`).parentElement;
        if (card) {
            card.remove();
        }
        
        // Refrescar lista si estábamos viendo la lista principal
        if (currentPage === 1) {
            loadPoems();
        }
        
        showSuccess('¡Poema borrado exitosamente!');
        
    } catch (error) {
        console.error('Error borrando poema:', error);
        showError(error.message || 'No se pudo borrar el poema');
    }
}

// ==============================
// Funciones internas para polling y gestión de estado
// ==============================

let pollingInterval = null;

function startPolling(poemaId, checkCallback, intervalMs) {
    stopPolling();
    
    pollingInterval = setInterval(() => {
        checkCallback(poemaId);
    }, intervalMs);
}

function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}
