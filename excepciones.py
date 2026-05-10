"""
=============================================================================
MÓDULO: excepciones.py
PROYECTO: Sistema Integral de Gestión - Software FJ
=============================================================================
Define la jerarquía completa de excepciones personalizadas del sistema.
Todas heredan de SoftwareFJError para permitir captura genérica o específica.

Principios aplicados:
  - Herencia       : jerarquía de excepciones propias
  - Encapsulación  : cada error agrupa código, mensaje y timestamp
  - Encadenamiento : usadas con "raise X from e" en los demás módulos
=============================================================================
"""

from datetime import datetime


# ─── EXCEPCIÓN BASE ───────────────────────────────────────────────────────────

class SoftwareFJError(Exception):
    """
    Clase base de todas las excepciones personalizadas de Software FJ.
    Encapsula un código de error, un mensaje descriptivo y la marca de tiempo.
    """

    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL"):
        self.mensaje   = mensaje
        self.codigo    = codigo
        self.timestamp = datetime.now()
        super().__init__(mensaje)

    def __str__(self) -> str:
        return f"[{self.codigo}] {self.mensaje}"


# ─── EXCEPCIONES ESPECÍFICAS ──────────────────────────────────────────────────

class ClienteInvalidoError(SoftwareFJError):
    """Datos de cliente inválidos o incompletos (nombre, correo, teléfono)."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_CLIENTE")


class ServicioInvalidoError(SoftwareFJError):
    """Configuración incorrecta de un servicio (precio, capacidad, stock)."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_SERVICIO")


class ReservaInvalidaError(SoftwareFJError):
    """Reserva que no puede crearse, confirmarse ni cancelarse."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_RESERVA")


class ServicioNoDisponibleError(SoftwareFJError):
    """Servicio que no está en estado ACTIVO al momento de la reserva."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_NO_DISPONIBLE")


class CalculoCostoError(SoftwareFJError):
    """Cálculo de costos con parámetros inválidos (descuento > 1, horas ≤ 0)."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_COSTO")


class ParametroFaltanteError(SoftwareFJError):
    """Parámetro obligatorio ausente o con valor None."""
    def __init__(self, parametro: str):
        super().__init__(
            f"El parámetro '{parametro}' es obligatorio y no fue proporcionado.",
            "ERR_PARAMETRO"
        )


class OperacionNoPermitidaError(SoftwareFJError):
    """Acción prohibida según el estado actual de la entidad."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_OPERACION")
