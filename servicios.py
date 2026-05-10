"""
=============================================================================
MÓDULO: servicios.py
PROYECTO: Sistema Integral de Gestión - Software FJ
=============================================================================
Define:
  - Servicio        : clase abstracta base para todos los servicios
  - ReservaSala     : reserva de salas de reuniones
  - AlquilerEquipo  : alquiler de equipos tecnológicos
  - AsesoriaTecnica : asesoría especializada con consultor asignado

Principios aplicados:
  - Herencia      : los tres servicios concretos heredan de Servicio
  - Polimorfismo  : cada uno sobreescribe calcular_costo(), describir(),
                    validar() e info_adicional() con su propia lógica
  - Encapsulación : atributos protegidos con @property
  - Abstracción   : Servicio define la interfaz; las subclases la implementan
=============================================================================
"""

from abc import ABC, abstractmethod
from typing import Optional

from entidades import EntidadBase
from excepciones import (
    ServicioInvalidoError,
    ServicioNoDisponibleError,
    CalculoCostoError,
    ParametroFaltanteError,
)
from logger import logger


# ─────────────────────────────────────────────────────────────────────────────
# CLASE ABSTRACTA: Servicio
# ─────────────────────────────────────────────────────────────────────────────

class Servicio(EntidadBase, ABC):
    """
    Clase abstracta que representa un servicio ofrecido por Software FJ.

    Hereda de EntidadBase y define los contratos que deben cumplir todos
    los servicios concretos.

    Método sobrecargado (simulado con parámetros opcionales):
        calcular_costo(horas)
        calcular_costo(horas, descuento=0.10)
        calcular_costo(horas, descuento=0.10, aplicar_impuesto=False)
    """

    ESTADO_ACTIVO     = "ACTIVO"
    ESTADO_INACTIVO   = "INACTIVO"
    ESTADO_SUSPENDIDO = "SUSPENDIDO"

    def __init__(self, nombre: str, precio_hora: float, descripcion: str = ""):
        """
        Constructor base del servicio.

        Lanza:
            ParametroFaltanteError : si el nombre está vacío.
            ServicioInvalidoError  : si el precio es <= 0.
        """
        super().__init__()

        if not nombre or not nombre.strip():
            raise ParametroFaltanteError("nombre del servicio")
        self._nombre = nombre.strip()

        if precio_hora <= 0:
            raise ServicioInvalidoError(
                f"El precio por hora debe ser mayor a 0. Recibido: {precio_hora}"
            )
        self._precio_hora = float(precio_hora)
        self._descripcion = descripcion.strip()
        self._estado      = self.ESTADO_ACTIVO

        logger.debug(
            f"Servicio creado: [{self.__class__.__name__}] "
            f"'{self._nombre}' — ${self._precio_hora}/h"
        )

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def precio_hora(self) -> float:
        return self._precio_hora

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @property
    def estado(self) -> str:
        return self._estado

    @estado.setter
    def estado(self, nuevo_estado: str):
        estados_validos = {self.ESTADO_ACTIVO, self.ESTADO_INACTIVO, self.ESTADO_SUSPENDIDO}
        if nuevo_estado not in estados_validos:
            raise ServicioInvalidoError(
                f"Estado '{nuevo_estado}' no válido. Use: {estados_validos}"
            )
        self._estado = nuevo_estado
        logger.info(f"Servicio '{self._nombre}' → estado: {nuevo_estado}")

    @property
    def disponible(self) -> bool:
        return self._estado == self.ESTADO_ACTIVO

    # ── Método sobrecargado: calcular_costo ───────────────────────────────────

    def calcular_costo(
        self,
        horas: float,
        descuento: float = 0.0,
        impuesto: float = 0.19,
        aplicar_impuesto: bool = True
    ) -> float:
        """
        Calcula el costo total del servicio.

        Variantes (sobrecarga simulada con parámetros opcionales):
          V1 — calcular_costo(horas)
               Precio base con IVA del 19%.
          V2 — calcular_costo(horas, descuento=0.10)
               Aplica 10% de descuento antes del IVA.
          V3 — calcular_costo(horas, descuento=0.10, aplicar_impuesto=False)
               Descuento sin IVA (clientes exentos).

        Parámetros:
            horas            (float): Duración — debe ser > 0.
            descuento        (float): Fracción 0.0–1.0 (default 0%).
            impuesto         (float): Fracción 0.0–1.0 (default 19% IVA Colombia).
            aplicar_impuesto (bool) : Si False, no se suma el impuesto.

        Lanza:
            CalculoCostoError: si algún parámetro está fuera de rango.
        """
        try:
            if horas <= 0:
                raise CalculoCostoError(
                    f"Las horas deben ser positivas. Recibido: {horas}"
                )
            if not (0.0 <= descuento <= 1.0):
                raise CalculoCostoError(
                    f"El descuento debe estar entre 0.0 y 1.0. Recibido: {descuento}"
                )
            if not (0.0 <= impuesto <= 1.0):
                raise CalculoCostoError(
                    f"El impuesto debe estar entre 0.0 y 1.0. Recibido: {impuesto}"
                )

            costo_base   = self._precio_hora * horas
            desc_val     = costo_base * descuento
            subtotal     = costo_base - desc_val
            impuesto_val = subtotal * impuesto if aplicar_impuesto else 0.0
            total        = subtotal + impuesto_val

            logger.debug(
                f"Costo '{self._nombre}': base=${costo_base:.2f} | "
                f"desc=${desc_val:.2f} | IVA=${impuesto_val:.2f} | "
                f"TOTAL=${total:.2f}"
            )
            return round(total, 2)

        except CalculoCostoError:
            raise
        except Exception as e:
            raise CalculoCostoError(
                f"Error inesperado en cálculo de costo: {e}"
            ) from e

    # ── Métodos abstractos ────────────────────────────────────────────────────

    @abstractmethod
    def describir(self) -> str:
        """Descripción completa del servicio."""
        pass

    @abstractmethod
    def validar(self) -> bool:
        """Valida que el servicio esté correctamente configurado."""
        pass

    @abstractmethod
    def info_adicional(self) -> str:
        """Información específica del tipo de servicio (polimorfismo)."""
        pass

    def verificar_disponibilidad(self):
        """
        Verifica que el servicio esté activo antes de una reserva.
        Lanza ServicioNoDisponibleError si no está en estado ACTIVO.
        """
        if not self.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._nombre}' no está disponible "
                f"(estado: {self._estado})."
            )

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"('{self._nombre}', ${self._precio_hora}/h, {self._estado})"
        )


# ─────────────────────────────────────────────────────────────────────────────
# SERVICIO 1: Reserva de Sala
# ─────────────────────────────────────────────────────────────────────────────

class ReservaSala(Servicio):
    """
    Servicio de reserva de salas de reuniones/conferencias.

    Atributos adicionales:
        capacidad  (int) : Aforo máximo de personas.
        tiene_tv   (bool): Pantalla/proyector disponible.
        tiene_wifi (bool): Conexión WiFi disponible.

    Comportamiento especial en calcular_costo():
        Si personas > 10 → recargo del 15% sobre el total calculado.
    """

    def __init__(
        self,
        nombre: str,
        precio_hora: float,
        capacidad: int,
        tiene_tv: bool = False,
        tiene_wifi: bool = True,
        descripcion: str = ""
    ):
        """
        Lanza:
            ServicioInvalidoError: si la capacidad es <= 0.
        """
        super().__init__(nombre, precio_hora, descripcion)

        if capacidad <= 0:
            raise ServicioInvalidoError(
                f"La capacidad de la sala debe ser mayor a 0. Recibido: {capacidad}"
            )
        self._capacidad  = int(capacidad)
        self._tiene_tv   = bool(tiene_tv)
        self._tiene_wifi = bool(tiene_wifi)

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def capacidad(self) -> int:
        return self._capacidad

    @property
    def tiene_tv(self) -> bool:
        return self._tiene_tv

    @property
    def tiene_wifi(self) -> bool:
        return self._tiene_wifi

    # ── Método sobrescrito: calcular_costo ────────────────────────────────────

    def calcular_costo(
        self,
        horas: float,
        descuento: float = 0.0,
        impuesto: float = 0.19,
        aplicar_impuesto: bool = True,
        personas: int = 1           # Parámetro extra: asistentes esperados
    ) -> float:
        """
        Calcula el costo de la sala.
        Si personas > 10 → aplica recargo del 15% sobre el total.

        Lanza:
            ServicioInvalidoError: si personas supera la capacidad de la sala.
            CalculoCostoError    : si hay error en el cálculo base.
        """
        try:
            if personas > self._capacidad:
                raise ServicioInvalidoError(
                    f"La sala '{self._nombre}' tiene capacidad para "
                    f"{self._capacidad} personas. Solicitado: {personas}."
                )

            costo = super().calcular_costo(horas, descuento, impuesto, aplicar_impuesto)

            # Recargo del 15% para grupos de más de 10 personas
            if personas > 10:
                recargo = costo * 0.15
                costo  += recargo
                logger.debug(
                    f"Recargo grupo grande ({personas} personas): "
                    f"+${recargo:.2f}"
                )

            return round(costo, 2)

        except ServicioInvalidoError:
            raise
        except Exception as e:
            raise CalculoCostoError(
                f"Error calculando costo de sala: {e}"
            ) from e

    # ── Métodos abstractos implementados ──────────────────────────────────────

    def describir(self) -> str:
        tv_txt   = "✔ TV/Proyector" if self._tiene_tv   else "✘ Sin TV"
        wifi_txt = "✔ WiFi"         if self._tiene_wifi else "✘ Sin WiFi"
        return (
            f"[SALA #{self._id}] {self._nombre} | "
            f"Capacidad: {self._capacidad} personas | "
            f"${self._precio_hora:,.0f}/h | {tv_txt} | {wifi_txt} | "
            f"Estado: {self._estado}"
        )

    def validar(self) -> bool:
        return bool(self._nombre) and self._precio_hora > 0 and self._capacidad > 0

    def info_adicional(self) -> str:
        equipos = []
        if self._tiene_tv:   equipos.append("TV/Proyector")
        if self._tiene_wifi: equipos.append("WiFi")
        eq_txt = ", ".join(equipos) if equipos else "Sin equipamiento adicional"
        return (
            f"Sala de reuniones | Cap: {self._capacidad} personas | "
            f"Equipamiento: {eq_txt}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# SERVICIO 2: Alquiler de Equipo
# ─────────────────────────────────────────────────────────────────────────────

class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos (laptops, proyectores, etc.).

    Atributos adicionales:
        tipo_equipo (str): Tipo/modelo del equipo.
        stock       (int): Unidades disponibles para alquiler.

    Comportamiento especial en calcular_costo():
        Si unidades >= 3 → descuento adicional del 10% automático.
    """

    def __init__(
        self,
        nombre: str,
        precio_hora: float,
        tipo_equipo: str,
        stock: int = 1,
        descripcion: str = ""
    ):
        """
        Lanza:
            ParametroFaltanteError: si tipo_equipo está vacío.
            ServicioInvalidoError : si stock <= 0.
        """
        super().__init__(nombre, precio_hora, descripcion)

        if not tipo_equipo or not tipo_equipo.strip():
            raise ParametroFaltanteError("tipo_equipo")
        self._tipo_equipo = tipo_equipo.strip()

        if stock <= 0:
            raise ServicioInvalidoError(
                f"El stock debe ser mayor a 0. Recibido: {stock}"
            )
        self._stock = int(stock)

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def tipo_equipo(self) -> str:
        return self._tipo_equipo

    @property
    def stock(self) -> int:
        return self._stock

    def reducir_stock(self, cantidad: int = 1):
        """
        Reduce el stock al confirmar un alquiler.
        Lanza ServicioNoDisponibleError si no hay suficientes unidades.
        """
        if cantidad > self._stock:
            raise ServicioNoDisponibleError(
                f"Stock insuficiente para '{self._nombre}'. "
                f"Disponibles: {self._stock} | Solicitados: {cantidad}"
            )
        self._stock -= cantidad
        logger.debug(
            f"Stock de '{self._nombre}' reducido en {cantidad}. "
            f"Restante: {self._stock}"
        )

    # ── Método sobrescrito: calcular_costo ────────────────────────────────────

    def calcular_costo(
        self,
        horas: float,
        descuento: float = 0.0,
        impuesto: float = 0.19,
        aplicar_impuesto: bool = True,
        unidades: int = 1           # Parámetro extra: equipos a alquilar
    ) -> float:
        """
        Calcula el costo del alquiler.
        Si unidades >= 3 → descuento adicional automático del 10%.

        Lanza:
            CalculoCostoError         : si unidades <= 0.
            ServicioNoDisponibleError : si no hay stock suficiente.
        """
        try:
            if unidades <= 0:
                raise CalculoCostoError(
                    f"El número de unidades debe ser mayor a 0. Recibido: {unidades}"
                )
            if unidades > self._stock:
                raise ServicioNoDisponibleError(
                    f"Solo hay {self._stock} unidad(es) disponibles de "
                    f"'{self._nombre}'."
                )

            # Descuento automático por volumen: 3+ unidades → +10% descuento
            descuento_total = descuento
            if unidades >= 3:
                descuento_total = min(descuento + 0.10, 1.0)
                logger.debug(
                    f"Descuento por volumen aplicado: +10% "
                    f"(total: {descuento_total * 100:.0f}%)"
                )

            costo_unitario = super().calcular_costo(
                horas, descuento_total, impuesto, aplicar_impuesto
            )
            total = round(costo_unitario * unidades, 2)

            logger.debug(
                f"Costo alquiler: {unidades} unid. × "
                f"${costo_unitario:.2f} = ${total:.2f}"
            )
            return total

        except (CalculoCostoError, ServicioNoDisponibleError):
            raise
        except Exception as e:
            raise CalculoCostoError(
                f"Error calculando costo de alquiler: {e}"
            ) from e

    # ── Métodos abstractos implementados ──────────────────────────────────────

    def describir(self) -> str:
        return (
            f"[EQUIPO #{self._id}] {self._nombre} | "
            f"Tipo: {self._tipo_equipo} | "
            f"Stock: {self._stock} unidades | "
            f"${self._precio_hora:,.0f}/h por unidad | "
            f"Estado: {self._estado}"
        )

    def validar(self) -> bool:
        return bool(self._nombre) and self._precio_hora > 0 and self._stock > 0

    def info_adicional(self) -> str:
        return (
            f"Alquiler de equipo | Tipo: {self._tipo_equipo} | "
            f"Stock disponible: {self._stock} unidades"
        )


# ─────────────────────────────────────────────────────────────────────────────
# SERVICIO 3: Asesoría Técnica
# ─────────────────────────────────────────────────────────────────────────────

class AsesoriaTecnica(Servicio):
    """
    Servicio de asesoría especializada con un consultor asignado.

    Atributos adicionales:
        especialidad (str): Área de especialización del asesor.
        consultor    (str): Nombre del consultor asignado.
        nivel        (str): BASICO | INTERMEDIO | AVANZADO.

    Comportamiento especial en calcular_costo():
        Aplica un multiplicador de precio según el nivel:
          BASICO      → ×1.0 (sin recargo)
          INTERMEDIO  → ×1.25 (+25%)
          AVANZADO    → ×1.60 (+60%)
    """

    MULTIPLICADORES_NIVEL = {
        "BASICO":     1.0,
        "INTERMEDIO": 1.25,
        "AVANZADO":   1.60,
    }

    def __init__(
        self,
        nombre: str,
        precio_hora: float,
        especialidad: str,
        consultor: str,
        nivel: str = "BASICO",
        descripcion: str = ""
    ):
        """
        Lanza:
            ParametroFaltanteError : si especialidad o consultor están vacíos.
            ServicioInvalidoError  : si el nivel no es válido.
        """
        super().__init__(nombre, precio_hora, descripcion)

        if not especialidad or not especialidad.strip():
            raise ParametroFaltanteError("especialidad")
        self._especialidad = especialidad.strip()

        if not consultor or not consultor.strip():
            raise ParametroFaltanteError("consultor")
        self._consultor = consultor.strip()

        nivel_upper = nivel.upper().strip()
        if nivel_upper not in self.MULTIPLICADORES_NIVEL:
            raise ServicioInvalidoError(
                f"Nivel '{nivel}' no válido. "
                f"Use: {list(self.MULTIPLICADORES_NIVEL.keys())}"
            )
        self._nivel = nivel_upper

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def especialidad(self) -> str:
        return self._especialidad

    @property
    def consultor(self) -> str:
        return self._consultor

    @property
    def nivel(self) -> str:
        return self._nivel

    # ── Método sobrescrito: calcular_costo ────────────────────────────────────

    def calcular_costo(
        self,
        horas: float,
        descuento: float = 0.0,
        impuesto: float = 0.19,
        aplicar_impuesto: bool = True,
        nivel_override: Optional[str] = None   # Permite cambiar nivel puntualmente
    ) -> float:
        """
        Calcula el costo de la asesoría aplicando el multiplicador del nivel.

        Parámetro adicional:
            nivel_override (str): Si se especifica, usa ese nivel en lugar
                                  del asignado al servicio.

        Lanza:
            CalculoCostoError: si el nivel_override no es válido.
        """
        try:
            nivel_a_usar = nivel_override.upper() if nivel_override else self._nivel
            if nivel_a_usar not in self.MULTIPLICADORES_NIVEL:
                raise CalculoCostoError(
                    f"Nivel override '{nivel_override}' no válido."
                )

            multiplicador = self.MULTIPLICADORES_NIVEL[nivel_a_usar]
            costo_base    = super().calcular_costo(
                horas, descuento, impuesto, aplicar_impuesto
            )
            total = round(costo_base * multiplicador, 2)

            logger.debug(
                f"Asesoría nivel {nivel_a_usar} | ×{multiplicador} | "
                f"base=${costo_base:.2f} → total=${total:.2f}"
            )
            return total

        except CalculoCostoError:
            raise
        except Exception as e:
            raise CalculoCostoError(
                f"Error calculando costo de asesoría: {e}"
            ) from e

    # ── Métodos abstractos implementados ──────────────────────────────────────

    def describir(self) -> str:
        return (
            f"[ASESORÍA #{self._id}] {self._nombre} | "
            f"Especialidad: {self._especialidad} | "
            f"Consultor: {self._consultor} | "
            f"Nivel: {self._nivel} | "
            f"${self._precio_hora:,.0f}/h base | "
            f"Estado: {self._estado}"
        )

    def validar(self) -> bool:
        return (
            bool(self._nombre) and
            self._precio_hora > 0 and
            bool(self._especialidad) and
            bool(self._consultor) and
            self._nivel in self.MULTIPLICADORES_NIVEL
        )

    def info_adicional(self) -> str:
        mult = self.MULTIPLICADORES_NIVEL[self._nivel]
        return (
            f"Asesoría especializada | Área: {self._especialidad} | "
            f"Consultor: {self._consultor} | "
            f"Nivel: {self._nivel} (×{mult} tarifa)"
        )
