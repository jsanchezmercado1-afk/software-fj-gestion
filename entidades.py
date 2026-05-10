"""
=============================================================================
MÓDULO: entidades.py
PROYECTO: Sistema Integral de Gestión - Software FJ
=============================================================================
Define:
  - EntidadBase : clase abstracta raíz del sistema (abstracción)
  - Cliente     : clase concreta con encapsulación y validaciones robustas

Principios aplicados:
  - Abstracción   : EntidadBase define el contrato mínimo del sistema
  - Herencia      : Cliente, Servicio y Reserva derivan de EntidadBase
  - Encapsulación : datos del cliente protegidos con @property y setters
  - Polimorfismo  : describir() y validar() se implementan de forma distinta
                    en cada subclase
=============================================================================
"""

import re
import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from excepciones import ClienteInvalidoError, ParametroFaltanteError
from logger import logger


# ─────────────────────────────────────────────────────────────────────────────
# CLASE ABSTRACTA BASE
# ─────────────────────────────────────────────────────────────────────────────

class EntidadBase(ABC):
    """
    Clase abstracta raíz del sistema Software FJ.

    Obliga a todas las entidades concretas (Cliente, Servicio, Reserva) a
    implementar describir() y validar(), garantizando un contrato mínimo
    de comportamiento en todo el sistema.
    """

    def __init__(self):
        # Identificador único de 8 caracteres en mayúsculas
        self._id: str = str(uuid.uuid4())[:8].upper()
        self._fecha_creacion: datetime = datetime.now()

    @property
    def id(self) -> str:
        """Identificador único de la entidad (solo lectura)."""
        return self._id

    @property
    def fecha_creacion(self) -> datetime:
        """Fecha y hora de creación de la entidad (solo lectura)."""
        return self._fecha_creacion

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción legible de la entidad."""
        pass

    @abstractmethod
    def validar(self) -> bool:
        """Verifica que la entidad esté correctamente configurada."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id})"


# ─────────────────────────────────────────────────────────────────────────────
# CLASE CLIENTE
# ─────────────────────────────────────────────────────────────────────────────

class Cliente(EntidadBase):
    """
    Representa un cliente registrado en el sistema de Software FJ.

    Encapsula datos personales con @property y setters que aplican
    validaciones estrictas antes de aceptar cualquier valor.
    """

    # Expresiones regulares de validación
    _REGEX_CORREO    = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$")
    _REGEX_TELEFONO  = re.compile(r"^\+?[\d\s\-]{7,15}$")

    def __init__(self, nombre: str, correo: str, telefono: str, empresa: str = ""):
        """
        Constructor del cliente con validación inmediata de todos los campos.

        Parámetros:
            nombre   (str): Nombre completo — obligatorio, mín. 3 caracteres.
            correo   (str): Correo electrónico — obligatorio, formato válido.
            telefono (str): Teléfono de contacto — obligatorio, solo dígitos.
            empresa  (str): Nombre de la empresa — opcional.

        Lanza:
            ParametroFaltanteError : si nombre, correo o teléfono están vacíos.
            ClienteInvalidoError   : si algún valor no pasa la validación.
        """
        super().__init__()

        # Usar los setters para aprovechar las validaciones
        self.nombre   = nombre
        self.correo   = correo
        self.telefono = telefono
        self._empresa = empresa.strip()

        logger.debug(f"Cliente creado: ID={self._id}, nombre='{self._nombre}'")

    # ── Propiedad: nombre ─────────────────────────────────────────────────────

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not valor.strip():
            raise ParametroFaltanteError("nombre")
        valor = valor.strip()
        if len(valor) < 3:
            raise ClienteInvalidoError(
                f"El nombre '{valor}' es demasiado corto (mínimo 3 caracteres)."
            )
        self._nombre = valor

    # ── Propiedad: correo ─────────────────────────────────────────────────────

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str):
        if not valor or not valor.strip():
            raise ParametroFaltanteError("correo")
        valor = valor.strip().lower()
        if not self._REGEX_CORREO.match(valor):
            raise ClienteInvalidoError(
                f"El correo '{valor}' no tiene formato válido (ej: usuario@dominio.com)."
            )
        self._correo = valor

    # ── Propiedad: teléfono ───────────────────────────────────────────────────

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor or not valor.strip():
            raise ParametroFaltanteError("telefono")
        valor = valor.strip()
        if not self._REGEX_TELEFONO.match(valor):
            raise ClienteInvalidoError(
                f"El teléfono '{valor}' no es válido. Use solo dígitos (7-15 caracteres)."
            )
        self._telefono = valor

    # ── Propiedad: empresa ────────────────────────────────────────────────────

    @property
    def empresa(self) -> str:
        return self._empresa

    # ── Métodos abstractos implementados ──────────────────────────────────────

    def describir(self) -> str:
        empresa_txt = f" | Empresa: {self._empresa}" if self._empresa else ""
        return (
            f"[CLIENTE #{self._id}] "
            f"Nombre: {self._nombre} | "
            f"Correo: {self._correo} | "
            f"Tel: {self._telefono}"
            f"{empresa_txt} | "
            f"Registrado: {self._fecha_creacion.strftime('%d/%m/%Y %H:%M')}"
        )

    def validar(self) -> bool:
        return bool(self._nombre and self._correo and self._telefono)

    def __str__(self) -> str:
        return f"Cliente({self._nombre}, {self._correo})"
