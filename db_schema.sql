-- =====================================================
-- Versario - Esquema SQL manual (para referencia)
-- =====================================================

-- Tabla: poemas
-- Almacena todos los poemas del usuario con su estado de generación
CREATE TABLE IF NOT EXISTS poemas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Información básica
    titulo TEXT NOT NULL,                    -- Título del poema
    autor TEXT,                              -- Autor (opcional)
    texto TEXT NOT NULL,                     -- Texto completo
    
    -- Archivo de audio generado
    ruta_audio TEXT,                         -- Ruta relativa al MP3
    
    -- Configuración TTS
    voz TEXT NOT NULL,                       -- ID de la voz utilizada
    velocidad REAL DEFAULT 1.0,              -- Factor de velocidad (0.8-1.2x)
    
    -- Estado y timestamp
    estado TEXT DEFAULT 'pendiente' CHECK(estado IN ('pendiente', 'generando', 'listo', 'error')),
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    actualizado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Índices para búsqueda rápida
CREATE INDEX IF NOT EXISTS idx_poemas_titulo ON poemas(titulo);
CREATE INDEX IF NOT EXISTS idx_poemas_estado ON poemas(estado);
CREATE INDEX IF NOT EXISTS idx_poemas_creado_en ON poemas(creado_en DESC);

-- Vistas útiles

-- Vista de resumen con conteo por estado
CREATE VIEW IF NOT EXISTS vw_poemas_estados AS
SELECT 
    estado,
    COUNT(*) as cantidad
FROM poemas
GROUP BY estado;

-- Vista de últimos 10 poemas
CREATE VIEW IF NOT EXISTS vw_poemas_recientes AS
SELECT * FROM poemas
ORDER BY creado_en DESC
LIMIT 10;

-- =====================================================
-- Ejemplo: Insertar poema manual
-- =====================================================
-- INSERT INTO poemas (titulo, autor, texto, voz, velocidad) VALUES 
-- ('Mi Pequeño Mundo', 'Juan Pérez', 
--  'Yo soy un mundo pequeño y feliz,
--   Con estrellas de azúcar en la boca.
--   Las nubes son algodón de colores,
--   Y el viento me dice sus historias.',
--  'es_ES_bahnc', 1.0);
