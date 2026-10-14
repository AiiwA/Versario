/**
 * Versario - Frontend Application
 * Maneja interacción con el backend API de FastAPI
 */

(function() {
    'use strict';

    // -------------------------------------------------------------------------
    // Configuración y constantes
    // -------------------------------------------------------------------------
    const API_BASE = '/api/poemas/';
    const VOICES_API = '/api/voices';
    const MAX_TEXT_LENGTH = 10000;
    
    // Estado de la aplicación
    let appState = {
        voices: [],
        currentPoemId: null,
        pollingInterval: null
    };

    // -------------------------------------------------------------------------
    // Inicialización
    // -------------------------------------------------------------------------
    
    document.addEventListener('DOMContentLoaded', function() {
        init();
    });

    function init() {
        checkPoemPage();
        loadVoices();
        setupEventListeners();
    }

    function checkPoemPage() {
        // Verificar si estamos en página de detalle de poema
        const route = window.location.pathname;
        
        if (route.includes('/poema/')) {
            // Extraer ID del URL y mostrar reproductor existente
            const match = route.match(/\/poema\/(\d+)/);
            if (match) {
                const poemId = parseInt(match[1]);
                appState.currentPoemId = poemId;
                
                document.getElementById('audioPlayer').src = `/api/poemas/${poemId}/audio`;
                document.getElementById('loadingSpinner').style.display = 'none';
            }
        } else {
            // Página principal - limpiar estado de polling anterior si existe
            if (appState.pollingInterval) {
                clearInterval(appState.pollingInterval);
                appState.pollingInterval = null;
            }
        }
    }

    // -------------------------------------------------------------------------
    // Cargar voces disponibles del API
    // -------------------------------------------------------------------------
    
    function loadVoices() {
        const voicesSelect = document.getElementById('voz');
        
        fetch(VOICES_API)
            .then(response => response.json())
            .then(voices => {
                appState.voices = voices;
                
                if (voices.length > 0) {
                    // Crear opciones de voces
                    const voiceOptions = voices.map(v => 
                        `<option value="${escapeHtml(v.name)}">${v.language} (${v.quality})</option>`
                    ).join('');
                    
                    if (voicesSelect) {
                        voicesSelect.innerHTML = voiceOptions;
                    }
                } else {
                    // Voces no disponibles
                    const defaultOption = '<option value="es_ES-davefx-medium">Voz predeterminada</option>';
                    if (voicesSelect) {
                        voicesSelect.innerHTML = defaultOption;
                    }
                }
            })
            .catch(error => {
                console.error('Error cargando voces:', error);
                // Vocas por defecto
                const defaultVoices = [{name: 'es_ES-davefx-medium'}];
                appState.voices = defaultVoices;
                loadDefaultVoiceOption();
            });
    }

    function loadDefaultVoiceOption() {
        const voicesSelect = document.getElementById('voz');
        if (voicesSelect) {
            voicesSelect.innerHTML = '<option value="es_ES-davefx-medium">Voz predeterminada</option>';
        }
    }

    // -------------------------------------------------------------------------
    // Manejadores de eventos del formulario
    // -------------------------------------------------------------------------
    
    function setupEventListeners() {
        const form = document.getElementById('poemForm');
        const textoInput = document.getElementById('texto');
        const textoCounter = document.getElementById('textoCounter');
        
        if (form) {
            form.addEventListener('submit', handleFormSubmit);
            
            // Actualizar contador de caracteres mientras se escribe
            if (textoInput && textoCounter) {
                textoInput.addEventListener('input', updateTextCounter);
            }
        }
    }

    function updateTextCounter() {
        const texto = document.getElementById('texto');
        const counter = document.getElementById('textoCounter');
        
        if (texto && counter) {
            const charCount = texto.value.length;
            counter.textContent = `${charCount}/${MAX_TEXT_LENGTH} caracteres`;
            
            // Cambiar color si está cerca del límite
            if (charCount > MAX_TEXT_LENGTH * 0.8) {
                counter.style.color = '#f44336';
            } else if (charCount > MAX_TEXT_REDIRECT) {
                counter.style.color = 'var(--success-color)';
            }
        }
    }

    // -------------------------------------------------------------------------
    // Manejar envío de formulario
    // -------------------------------------------------------------------------
    
    function handleFormSubmit(event) {
        event.preventDefault();
        
        const form = document.getElementById('poemForm');
        
        if (!form) return;
        
        // Validar antes de enviar
        const validation = validateInput();
        
        if (!validation.valid) {
            showValidationErrors(validation.errors);
            return;
        }
        
        // Recopilar datos del formulario
        const poemData = collectFormData(form);
        
        // Crear poema vía API
        createPoem(poemData)
            .then(response => {
                if (response && response.id !== null) {
                    // Redirigir a página de detalle
                    window.location.href = `/poema/${response.id}`;
                } else {
                    showError('Error al crear el poema');
                }
            })
            .catch(error => {
                console.error('Error creando poema:', error);
                showError('Error de conexión con el servidor. Intenta nuevamente.');
            });
    }

    function validateInput() {
        const titulo = document.getElementById('titulo')?.value || '';
        const texto = document.getElementById('texto')?.value || '';
        const velocidad = parseFloat(document.getElementById('velocidad')?.value) || 1.0;
        
        const errors = [];
        
        if (!titulo.trim()) {
            errors.push('Título no puede estar vacío');
        }
        
        if (texto.length > MAX_TEXT_LENGTH) {
            errors.push(`Texto máximo ${MAX_TEXT_LENGTH} caracteres`);
        }
        
        if (velocidad < 0.8 || velocidad > 1.2) {
            errors.push('Velocidad debe estar entre 0.8 y 1.2');
        }
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }

    function showValidationErrors(errors) {
        // Mostrar errores al usuario (implementación simple)
        console.error('Errores de validación:', errors);
        alert(`Errores:\n${errors.join('\n')}`);
    }

    function collectFormData(form) {
        const formData = new FormData(form);
        
        return {
            titulo: formData.get('titulo'),
            autor: formData.get('autor') || null,
            texto: formData.get('texto'),
            voz: formData.get('voz'),
            velocidad: parseFloat(formData.get('velocidad'))
        };
    }

    // -------------------------------------------------------------------------
    // Crear poema vía API POST
    // -------------------------------------------------------------------------
    
    function createPoem(data) {
        return fetch(API_BASE, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                return response.json().catch(() => ({}));
            }
        })
        .catch(error => {
            console.error('Error POST /api/poemas/:', error);
            throw error;
        });
    }

    // -------------------------------------------------------------------------
    // Mostrar errores de polling
    // -------------------------------------------------------------------------
    
    function showError(message) {
        const modal = document.getElementById('errorModal');
        const errorMsg = document.getElementById('errorMessage');
        
        if (modal && errorMsg) {
            errorMsg.textContent = message;
            modal.style.display = 'block';
        } else {
            console.error('Error:', message);
        }
    }

    // -------------------------------------------------------------------------
    // Utilidades
    // -------------------------------------------------------------------------
    
    function escapeHtml(text) {
        if (!text) return text;
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

})();
