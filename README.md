# 🎵 Versario - Generador de Poemas Audio

Versario convierte poemas escritos en texto a audio con síntesis de voz, aplicando pausas poéticas naturales entre estrofas y versos, reproductor web integrado con resaltado sincronizado y opción de descarga de audio.

## ✨ Características

- 🎯 **Conversión de texto a audio**: Síntesis de voz con velocidad configurable (0.8x - 1.2x) y selección de voces en español.
- 📝 **Pausas poéticas naturales**:
  - 400 ms de pausa entre versos consecutivos.
  - 1000 ms de pausa entre estrofas (separadas por doble salto de línea `\n\n`).
- 🎨 **Resaltado interactivo en tiempo real**: Los versos se iluminan a medida que son recitados y se puede hacer clic en cualquier verso para escucharlo individualmente.
- 💾 **Descarga de audio**: Exportación directa de archivos de audio estructurados (`.wav`).
- 📚 **Biblioteca local de poemas**: Persistencia en almacenamiento local (`localStorage`) para consultar, reproducir y gestionar los poemas creados.
- 📖 **Poemas de ejemplo integrados**: Botones de inserción rápida para *Soneto del Alba* (R.L. Stevenson), *La Cenicienta* y *El Viaje*.
- 💎 **Diseño fiel y accesible**: Conserva fielmente la paleta visual, estilos y estructura original de Versario con React, TypeScript y Tailwind CSS.

## 🚀 Inicio Rápido

### Requisitos previos
- Node.js 20+ o 22+
- npm

### Instalación y ejecución

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo en http://localhost:3000
npm run dev

# Compilar para producción
npm run build

# Validar TypeScript y linter
npm run lint
```

## 📖 Uso

1. **Crear Poema**:
   - Ingresa el **Título** (obligatorio).
   - Ingresa el **Autor** (opcional, por defecto 'Anónimo').
   - Escribe o pega el **Texto del poema** (usa doble salto de línea para separar estrofas; cada línea no vacía es un verso).
   - Ajusta la **Velocidad** (0.8x a 1.2x).
   - Selecciona la **Voz** deseada.
   - Haz clic en **"Crear Poema"** (o carga uno de los ejemplos con un solo clic).

2. **Reproducción y Descarga**:
   - Pulsa **"▶ Reproducir"** para escuchar la declamación con pausas poéticas y seguimiento visual.
   - Pulsa **"⬇ Descargar Audio"** para obtener el archivo de audio.
   - Pulsa **"← Volver"** para regresar a la lista de poemas y crear nuevos textos.

## 🛠️ Tecnologías

- **React 19** + **TypeScript**
- **Vite 6**
- **Tailwind CSS v4**
- **Web Speech API & Web Audio API**
- **Lucide React**

## 📝 Licencia

MIT License.
