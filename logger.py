"""
=============================================================================
MÓDULO: logger.py
PROYECTO: Sistema Integral de Gestión - Software FJ
=============================================================================
Configura y expone el objeto logger global del sistema.
Escribe simultáneamente en archivo (.log) y en la consola.

Niveles:
  - DEBUG  → archivo  (captura absolutamente todo)
  - INFO   → consola  (solo lo relevante para el usuario)
=============================================================================
"""

import os
import logging
from datetime import datetime


def configurar_logger() -> logging.Logger:
    """
    Crea y configura el logger principal de Software FJ.
    El archivo de log se nombra con la fecha del día (rotación diaria natural).

    Retorna:
        logging.Logger: instancia lista para usar en todo el proyecto.
    """

    # Crear carpeta logs/ si no existe
    os.makedirs("logs", exist_ok=True)

    fecha_hoy = datetime.now().strftime("%Y%m%d")
    ruta_log  = f"logs/software_fj_{fecha_hoy}.log"

    formato = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)-8s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.DEBUG)

    # Evitar duplicar handlers si el módulo se importa varias veces
    if logger.handlers:
        return logger

    # Handler 1: archivo — guarda TODO desde DEBUG
    handler_archivo = logging.FileHandler(ruta_log, encoding="utf-8")
    handler_archivo.setLevel(logging.DEBUG)
    handler_archivo.setFormatter(formato)

    # Handler 2: consola — solo INFO y superiores
    handler_consola = logging.StreamHandler()
    handler_consola.setLevel(logging.INFO)
    handler_consola.setFormatter(formato)

    logger.addHandler(handler_archivo)
    logger.addHandler(handler_consola)

    return logger


# Instancia global — importar desde los demás módulos así:
#   from logger import logger
logger = configurar_logger()
