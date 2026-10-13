"""
Configuración de base de datos SQLite para Versario.
Inicializa la base de datos y define las tablas necesarias.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexión a SQLite (archivos en /audio para mantenerlo simple)
DATABASE_URL = "sqlite:///./poemas.db"

# Crear engine con parametrizado de consultas
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Permitir conexiones concurrentes
    echo=False  # Poner True para debug (logging de SQL)
)

# Sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para las clases mapeadas a tablas
Base = declarative_base()


def get_db():
    """
    Dependencia FastAPI para obtener una sesión de DB.
    Se usa con @Depends en los endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """
    Inicializa la base de datos creando las tablas si no existen.
    Debe llamarse al inicio de la aplicación.
    """
    Base.metadata.create_all(bind=engine)
