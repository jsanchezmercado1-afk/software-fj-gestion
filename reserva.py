"""
=============================================================================
MÓDULO: reserva.py
PROYECTO: Sistema Integral de Gestión - Software FJ
=============================================================================
Define la clase Reserva que integra Cliente + Servicio + duración + estado.
Implementa el flujo completo:
    PENDIENTE → CONFIRMADA → COMPLETADA
                          ↘ CANCELADA

Manejo de excepciones aplicado:
  - try/except         : captura errores puntuales al confirmar/procesar
  - try/except/else    : bloque de éxito separado (confirmar)
  - try/except/finally : limpieza garantizada (cancelar)
  - Encadenamiento     : raise X from e para trazabilidad completa
=============================================================================
"""

from datetime import datetime, timedelta
from typing import Optional

from entidades import EntidadBase, Cliente
from servicios import Servicio
from excepciones import (
    ReservaInvalidaError,
    ServicioNoDisponibleError,
    OperacionNoPermitidaError,
    CalculoCostoError,
    ParametroFaltanteError,
)
from logger import logger


class Reserva(EntidadBase):
    """
    Representa una reserva en el sistema de Software FJ.

    Integra un Cliente con un Servicio, define la duración y gestiona
    el ciclo de vida completo de la reserva.
    """

    ESTADO_PENDIENTE  = "PENDIENTE"
    ESTADO_CONFIRMADA = "CONFIRMADA"
    ESTADO_COMPLETADA = "COMPLETADA"
    ESTADO_CANCELADA  = "CANCELADA"

    def __init__(
        self,
        cliente: Cliente,
        servicio: Servicio,
        horas: float,
        fecha_inicio: Optional[datetime] = None,
        notas: str = ""
    ):
        """
        Crea una nueva reserva vinculando cliente y servicio.

        Parámetros:
            cliente      (Cliente) : Objeto Cliente validado.
            servicio     (Servicio): Objeto Servicio (cualquier subclase).
            horas        (float)   : Duración en horas (debe ser > 0).
            fecha_inicio (datetime): Fecha/hora de inicio (default: ahora).
            notas        (str)     : Observaciones opcionales.

        Lanza:
            ParametroFaltanteError   : si cliente o servicio son None.
            ReservaInvalidaError     : si horas <= 0.
            ServicioNoDisponibleError: si el servicio no está activo.
        """
        super().__init__()

        if cliente is None:
            raise ParametroFaltanteError("cliente")
        if servicio is None:
            raise ParametroFaltanteError("servicio")
        if horas <= 0:
            raise ReservaInvalidaError(
                f"La duración debe ser mayor a 0 horas. Recibido: {horas}"
            )

        # Delega la verificación de disponibilidad al servicio (polimorfismo)
        servicio.verificar_disponibilidad()

        self._cliente             = cliente
        self._servicio            = servicio
        self._horas               = float(horas)
        self._fecha_inicio        = fecha_inicio if fecha_inicio else datetime.now()
        self._fecha_fin           = self._fecha_inicio + timedelta(hours=self._horas)
        self._notas               = notas.strip()
        self._estado              = self.ESTADO_PENDIENTE
        self._costo_total         = 0.0
        self._fecha_confirmacion  = None
        self._fecha_cancelacion   = None

        logger.info(
            f"Reserva #{self._id} CREADA | "
            f"Cliente: {cliente.nombre} | "
            f"Servicio: {servicio.nombre} | "
            f"Duración: {horas}h"
        )

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def horas(self) -> float:
        return self._horas

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    @property
    def fecha_inicio(self) -> datetime:
        return self._fecha_inicio

    @property
    def fecha_fin(self) -> datetime:
        return self._fecha_fin

    # ── CONFIRMAR RESERVA ─────────────────────────────────────────────────────

    def confirmar(self, descuento: float = 0.0, aplicar_impuesto: bool = True) -> float:
        """
        Confirma la reserva y calcula el costo total.
        Solo puede confirmarse si está en estado PENDIENTE.

        Usa try/except/else: el bloque else solo se ejecuta si no hubo error,
        separando claramente el manejo de errores del flujo exitoso.

        Parámetros:
            descuento        (float): Descuento a aplicar (0.0–1.0).
            aplicar_impuesto (bool) : Si incluir IVA en el cálculo.

        Retorna:
            float: Costo total de la reserva confirmada.

        Lanza:
            OperacionNoPermitidaError: si la reserva no está en PENDIENTE.
            CalculoCostoError        : si el cálculo de costo falla.
        """
        try:
            if self._estado != self.ESTADO_PENDIENTE:
                raise OperacionNoPermitidaError(
                    f"No se puede confirmar la reserva #{self._id} "
                    f"en estado '{self._estado}'. Debe estar en PENDIENTE."
                )

            costo = self._servicio.calcular_costo(
                horas=self._horas,
                descuento=descuento,
                aplicar_impuesto=aplicar_impuesto
            )

        except (OperacionNoPermitidaError, CalculoCostoError):
            raise

        except Exception as e:
            raise ReservaInvalidaError(
                f"Error inesperado al confirmar reserva #{self._id}: {e}"
            ) from e

        else:
            # Bloque else: se ejecuta SOLO si no hubo ninguna excepción
            self._costo_total       = costo
            self._estado            = self.ESTADO_CONFIRMADA
            self._fecha_confirmacion = datetime.now()

            logger.info(
                f"Reserva #{self._id} CONFIRMADA | "
                f"Cliente: {self._cliente.nombre} | "
                f"Servicio: {self._servicio.nombre} | "
                f"Costo: ${costo:,.2f} | "
                f"Descuento: {descuento * 100:.0f}%"
            )
            return costo

    # ── CANCELAR RESERVA ──────────────────────────────────────────────────────

    def cancelar(self, motivo: str = "Sin motivo especificado") -> bool:
        """
        Cancela la reserva. Solo es posible si está en PENDIENTE o CONFIRMADA.

        Usa try/except/finally: el bloque finally garantiza que siempre
        se registre el intento, independientemente del resultado.

        Parámetros:
            motivo (str): Razón de la cancelación.

        Retorna:
            bool: True si la cancelación fue exitosa.

        Lanza:
            OperacionNoPermitidaError: si la reserva está COMPLETADA o ya CANCELADA.
        """
        intento_exitoso = False

        try:
            estados_cancelables = {self.ESTADO_PENDIENTE, self.ESTADO_CONFIRMADA}
            if self._estado not in estados_cancelables:
                raise OperacionNoPermitidaError(
                    f"No se puede cancelar la reserva #{self._id} "
                    f"en estado '{self._estado}'. "
                    f"Solo se pueden cancelar reservas PENDIENTES o CONFIRMADAS."
                )

            self._estado           = self.ESTADO_CANCELADA
            self._fecha_cancelacion = datetime.now()
            intento_exitoso        = True

        except OperacionNoPermitidaError:
            raise

        finally:
            # Siempre se ejecuta: registrar el intento en el log
            if intento_exitoso:
                logger.info(
                    f"Reserva #{self._id} CANCELADA | "
                    f"Motivo: {motivo} | "
                    f"Cliente: {self._cliente.nombre}"
                )
            else:
                logger.warning(
                    f"Intento de cancelación FALLIDO para reserva #{self._id} "
                    f"(estado: {self._estado})"
                )

        return True

    # ── PROCESAR RESERVA ──────────────────────────────────────────────────────

    def procesar(self) -> bool:
        """
        Marca la reserva como COMPLETADA.
        Solo puede procesarse si está en estado CONFIRMADA.

        Retorna:
            bool: True si el procesamiento fue exitoso.

        Lanza:
            OperacionNoPermitidaError: si la reserva no está CONFIRMADA.
        """
        try:
            if self._estado != self.ESTADO_CONFIRMADA:
                raise OperacionNoPermitidaError(
                    f"La reserva #{self._id} debe estar CONFIRMADA para procesarse. "
                    f"Estado actual: '{self._estado}'."
                )

            self._estado = self.ESTADO_COMPLETADA
            logger.info(
                f"Reserva #{self._id} COMPLETADA | "
                f"Cliente: {self._cliente.nombre} | "
                f"Servicio: {self._servicio.nombre} | "
                f"Total cobrado: ${self._costo_total:,.2f}"
            )
            return True

        except OperacionNoPermitidaError:
            raise
        except Exception as e:
            raise ReservaInvalidaError(
                f"Error inesperado al procesar reserva #{self._id}: {e}"
            ) from e

    # ── Métodos abstractos implementados ──────────────────────────────────────

    def describir(self) -> str:
        costo_txt = f"${self._costo_total:,.2f}" if self._costo_total > 0 else "Pendiente"
        return (
            f"\n{'─' * 60}\n"
            f"  RESERVA #{self._id}  [{self._estado}]\n"
            f"{'─' * 60}\n"
            f"  Cliente  : {self._cliente.nombre} ({self._cliente.correo})\n"
            f"  Servicio : {self._servicio.nombre}\n"
            f"  Tipo     : {self._servicio.__class__.__name__}\n"
            f"  Info     : {self._servicio.info_adicional()}\n"
            f"  Inicio   : {self._fecha_inicio.strftime('%d/%m/%Y %H:%M')}\n"
            f"  Fin      : {self._fecha_fin.strftime('%d/%m/%Y %H:%M')}\n"
            f"  Duración : {self._horas}h\n"
            f"  Costo    : {costo_txt}\n"
            f"  Notas    : {self._notas if self._notas else '—'}\n"
            f"{'─' * 60}"
        )

    def validar(self) -> bool:
        return (
            self._cliente is not None and
            self._servicio is not None and
            self._horas > 0 and
            self._estado in {
                self.ESTADO_PENDIENTE, self.ESTADO_CONFIRMADA,
                self.ESTADO_COMPLETADA, self.ESTADO_CANCELADA
            }
        )

    def __str__(self) -> str:
        return (
            f"Reserva(#{self._id}, {self._cliente.nombre}, "
            f"{self._servicio.nombre}, {self._estado})"
        )
