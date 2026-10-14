"""Facade API - Centraliza todas las funcionalidades del programa."""

from .api import APIFacade, api_facade
from .models import FacadePoema

__all__ = ["APIFacade", "FacadePoema", "api_facade"]

# Exportar la instancia singleton
if 'api_facade' not in dir():
    # Importar desde aquí para evitar circular imports
    from . import api
