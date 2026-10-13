"""
Script para crear poemas de ejemplo en la base de datos.
Ejecutar con: python scripts/crear_poemas_ejemplo.py
"""
from pathlib import Path
import sys

def main():
    from app.database import get_db
    from app.models import Poema
    
    db = next(get_db())
    
    poemas = [
        {
            "titulo": "Soneto del Alba",
            "autor": "Robert Louis Stevenson",
            "texto": """Era noche oscura y tranquila
Y el viento susurraba en las ramas;
Una estrella parpadeaba en la calma.
¡Ay! ¡Cómo lloraba yo!

Y el alba dorada apareció,
Desatando los grillos del sueño;
El amanecer llegó con su fulgor.
""",
            "voz": "es_ES_bahnc",
            "velocidad": 1.0
        },
        {
            "titulo": "La Cenicienta (Fragmento)",
            "autor": "Anónimo",
            "texto": """Había una vez un pobre hombre
Con una casa y una pequeña parcela.
Él tenía tres hijas muy lindas,
Pero la más joven era la más triste.

Su madre había muerto hace mucho tiempo,
Deja huérfana a las niñas en soledad.
Y ella trabajaba duro cada día,
Limpiando y sirviendo a su familia.
""",
            "voz": "es_ES_damek",
            "velocidad": 0.95
        },
        {
            "titulo": "El Viaje",
            "autor": "Poema original",
            "texto": """El mar se extendía ante mis ojos,
Olas saltaban contra la roca gris;
El viento me cantaba historias antiguas,
De navegantes que antes vivieron aquí.

Los pájaros volaban en formación,
Sobre el horizonte azul y sereno;
La tierra me llamaba desde lejos,
Pero yo tenía que seguir yendo.
""",
            "voz": "es_ES_bahnc",
            "velocidad": 1.0
        }
    ]
    
    # Limpiar poemas existentes (opcional)
    print("🗑️  Borrando poemas existentes...")
    db.query(Poema).delete()
    db.commit()
    
    # Insertar nuevos poemas
    for poema_data in poemas:
        print(f"➕ Creando poema: {poema_data['titulo']}")
        
        poem = Poema(
            id=f"demo_{hash(poema_data['titulo']) % 10000:04d}",
            titulo=poema_data['titulo'],
            autor=poema_data['autor'],
            texto=poema_data['texto'],
            voz=poema_data['voz'],
            velocidad=float(poema_data['velocidad']),
            estado="pendiente",
            ruta_audio=None,
            creado_en=None
        )
        
        db.add(poema)
    
    db.commit()
    
    print(f"\n✅ {len(poemas)} poemas creados exitosamente!")
    print("\nPuedes verlos en: http://localhost:8000")


if __name__ == "__main__":
    main()
