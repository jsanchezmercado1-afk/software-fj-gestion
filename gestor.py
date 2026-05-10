"""
=============================================================================
MÓDULO: gestor.py
PROYECTO: Sistema Integral de Gestión - Software FJ
=============================================================================
Define GestorSistema: controlador central que administra las listas de
clientes, servicios y reservas.

Responsabilidades:
  - Registrar y buscar clientes
  - Agregar y buscar servicios
  - Crear, confirmar, cancelar y procesar reservas
  - Generar reportes del estado del sistema

Manejo de excepciones: todos los métodos capturan SoftwareFJError y
Exception para garantizar que el sistema nunca se detenga por un error.
=============================================================================
"""

from typing import List, Optional
from datetime import datetime

from entidades import Cliente
from servicios import Servicio
from reserva import Reserva
from excepciones import (
    ClienteInvalidoError,
    ServicioInvalidoError,
    SoftwareFJError,
)
from logger import logger


class GestorSistema:
    """
    Controlador central del Sistema de Gestión Software FJ.

    Administra tres listas internas:
        _clientes  : objetos Cliente registrados.
        _servicios : objetos Servicio disponibles.
        _reservas  : objetos Reserva creados.
    """

    def __init__(self):
        self._clientes:  List[Cliente]  = []
        self._servicios: List[Servicio] = []
        self._reservas:  List[Reserva]  = []

        logger.info("=" * 60)
        logger.info("  SOFTWARE FJ — Sistema de Gestión Iniciado")
        logger.info("=" * 60)

    # ─────────────────────────────────────────────────────────────────────────
    # GESTIÓN DE CLIENTES
    # ─────────────────────────────────────────────────────────────────────────

    def registrar_cliente(
        self, nombre: str, correo: str, telefono: str, empresa: str = ""
    ) -> Optional[Cliente]:
        """
        Registra un nuevo cliente verificando que el correo no esté duplicado.

        Retorna:
            Cliente: objeto creado si el registro fue exitoso.
            None   : si hubo algún error de validación.
        """
        try:
            for c in self._clientes:
                if c.correo == correo.strip().lower():
                    raise ClienteInvalidoError(
                        f"Ya existe un cliente con el correo '{correo}'."
                    )

            cliente = Cliente(nombre, correo, telefono, empresa)
            self._clientes.append(cliente)
            logger.info(f"✔ Cliente registrado: {cliente.nombre} (ID: {cliente.id})")
            return cliente

        except SoftwareFJError as e:
            logger.error(f"✘ Error al registrar cliente '{nombre}': {e}")
            return None

        except Exception as e:
            logger.error(f"✘ Error inesperado al registrar cliente '{nombre}': {e}")
            return None

    def buscar_cliente(self, correo: str) -> Optional[Cliente]:
        """Busca un cliente por correo electrónico (insensible a mayúsculas)."""
        correo_norm = correo.strip().lower()
        for cliente in self._clientes:
            if cliente.correo == correo_norm:
                return cliente
        return None

    def listar_clientes(self):
        """Imprime la lista completa de clientes registrados."""
        print(f"\n{'═' * 60}")
        print(f"  CLIENTES REGISTRADOS ({len(self._clientes)})")
        print(f"{'═' * 60}")
        if not self._clientes:
            print("  (Sin clientes registrados)")
        else:
            for i, c in enumerate(self._clientes, 1):
                print(f"  {i}. {c.describir()}")
        print()

    # ─────────────────────────────────────────────────────────────────────────
    # GESTIÓN DE SERVICIOS
    # ─────────────────────────────────────────────────────────────────────────

    def agregar_servicio(self, servicio: Servicio) -> bool:
        """
        Agrega un servicio al catálogo del sistema.

        Retorna:
            bool: True si fue agregado, False si hubo error.
        """
        try:
            if not isinstance(servicio, Servicio):
                raise ServicioInvalidoError(
                    "El objeto no es una instancia de Servicio."
                )
            if not servicio.validar():
                raise ServicioInvalidoError(
                    f"El servicio '{servicio.nombre}' no pasó la validación interna."
                )

            self._servicios.append(servicio)
            logger.info(
                f"✔ Servicio agregado: [{servicio.__class__.__name__}] "
                f"'{servicio.nombre}' (ID: {servicio.id})"
            )
            return True

        except SoftwareFJError as e:
            logger.error(f"✘ Error al agregar servicio: {e}")
            return False

        except Exception as e:
            logger.error(f"✘ Error inesperado al agregar servicio: {e}")
            return False

    def buscar_servicio(self, nombre: str) -> Optional[Servicio]:
        """Busca un servicio por nombre (búsqueda parcial, insensible a mayúsculas)."""
        nombre_norm = nombre.strip().lower()
        for servicio in self._servicios:
            if nombre_norm in servicio.nombre.lower():
                return servicio
        return None

    def listar_servicios(self):
        """Imprime el catálogo completo de servicios disponibles."""
        print(f"\n{'═' * 60}")
        print(f"  CATÁLOGO DE SERVICIOS ({len(self._servicios)})")
        print(f"{'═' * 60}")
        if not self._servicios:
            print("  (Sin servicios registrados)")
        else:
            for i, s in enumerate(self._servicios, 1):
                print(f"  {i}. {s.describir()}")
        print()

    # ─────────────────────────────────────────────────────────────────────────
    # GESTIÓN DE RESERVAS
    # ─────────────────────────────────────────────────────────────────────────

    def crear_reserva(
        self,
        cliente: Cliente,
        servicio: Servicio,
        horas: float,
        notas: str = ""
    ) -> Optional[Reserva]:
        """
        Crea una nueva reserva en estado PENDIENTE.

        Usa try/except/else: el bloque else solo se ejecuta si la
        creación fue exitosa, separando limpiamente el error del flujo normal.

        Retorna:
            Reserva: objeto creado si fue exitoso.
            None   : si hubo algún error.
        """
        try:
            reserva = Reserva(cliente, servicio, horas, notas=notas)

        except SoftwareFJError as e:
            logger.error(f"✘ Error al crear reserva: {e}")
            return None

        except Exception as e:
            logger.error(f"✘ Error inesperado al crear reserva: {e}")
            return None

        else:
            # Solo se ejecuta si NO hubo excepción
            self._reservas.append(reserva)
            logger.info(
                f"✔ Reserva #{reserva.id} creada para "
                f"'{cliente.nombre}' — Servicio: '{servicio.nombre}'"
            )
            return reserva

    def confirmar_reserva(
        self,
        reserva: Reserva,
        descuento: float = 0.0,
        aplicar_impuesto: bool = True
    ) -> bool:
        """
        Confirma una reserva existente y calcula su costo final.

        Usa try/except/finally: el bloque finally garantiza que siempre
        se registre el resultado del intento.

        Retorna:
            bool: True si fue confirmada, False si hubo error.
        """
        resultado = False

        try:
            costo     = reserva.confirmar(descuento, aplicar_impuesto)
            resultado = True
            print(f"  ✔ Reserva #{reserva.id} confirmada | Costo: ${costo:,.2f}")

        except SoftwareFJError as e:
            logger.error(f"✘ Error al confirmar reserva #{reserva.id}: {e}")

        except Exception as e:
            logger.error(f"✘ Error inesperado al confirmar reserva: {e}")

        finally:
            estado_log = "EXITOSO" if resultado else "FALLIDO"
            logger.debug(
                f"Intento de confirmación reserva #{reserva.id}: {estado_log}"
            )

        return resultado

    def cancelar_reserva(self, reserva: Reserva, motivo: str = "") -> bool:
        """
        Cancela una reserva existente.

        Retorna:
            bool: True si fue cancelada, False si hubo error.
        """
        try:
            reserva.cancelar(motivo)
            print(f"  ✔ Reserva #{reserva.id} cancelada. Motivo: {motivo}")
            return True

        except SoftwareFJError as e:
            logger.error(f"✘ Error al cancelar reserva #{reserva.id}: {e}")
            return False

    def procesar_reserva(self, reserva: Reserva) -> bool:
        """
        Procesa (completa) una reserva confirmada.

        Retorna:
            bool: True si fue procesada, False si hubo error.
        """
        try:
            reserva.procesar()
            print(f"  ✔ Reserva #{reserva.id} procesada y completada.")
            return True

        except SoftwareFJError as e:
            logger.error(f"✘ Error al procesar reserva #{reserva.id}: {e}")
            return False

    def listar_reservas(self, filtro_estado: str = ""):
        """
        Imprime todas las reservas, opcionalmente filtradas por estado.

        Parámetro:
            filtro_estado (str): PENDIENTE | CONFIRMADA | COMPLETADA | CANCELADA
        """
        reservas_mostrar = (
            [r for r in self._reservas if r.estado == filtro_estado.upper()]
            if filtro_estado else self._reservas
        )

        titulo = f"RESERVAS{' — ' + filtro_estado.upper() if filtro_estado else ''}"
        print(f"\n{'═' * 60}")
        print(f"  {titulo} ({len(reservas_mostrar)})")
        print(f"{'═' * 60}")

        if not reservas_mostrar:
            print("  (Sin reservas)")
        else:
            for r in reservas_mostrar:
                print(r.describir())
        print()

    # ─────────────────────────────────────────────────────────────────────────
    # REPORTE DEL SISTEMA
    # ─────────────────────────────────────────────────────────────────────────

    def reporte_general(self):
        """Imprime un resumen ejecutivo del estado del sistema."""
        confirmadas = sum(1 for r in self._reservas if r.estado == Reserva.ESTADO_CONFIRMADA)
        completadas = sum(1 for r in self._reservas if r.estado == Reserva.ESTADO_COMPLETADA)
        canceladas  = sum(1 for r in self._reservas if r.estado == Reserva.ESTADO_CANCELADA)
        pendientes  = sum(1 for r in self._reservas if r.estado == Reserva.ESTADO_PENDIENTE)
        ingresos    = sum(
            r.costo_total for r in self._reservas
            if r.estado in {Reserva.ESTADO_CONFIRMADA, Reserva.ESTADO_COMPLETADA}
        )

        print(f"\n{'═' * 60}")
        print(f"  REPORTE GENERAL — SOFTWARE FJ")
        print(f"  Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'═' * 60}")
        print(f"  Clientes registrados : {len(self._clientes)}")
        print(f"  Servicios en catálogo: {len(self._servicios)}")
        print(f"  Total de reservas    : {len(self._reservas)}")
        print(f"    - Pendientes       : {pendientes}")
        print(f"    - Confirmadas      : {confirmadas}")
        print(f"    - Completadas      : {completadas}")
        print(f"    - Canceladas       : {canceladas}")
        print(f"  Ingresos totales     : ${ingresos:>14,.2f}")
        print(f"{'═' * 60}\n")
        logger.info(
            f"Reporte: {len(self._reservas)} reservas | "
            f"Ingresos: ${ingresos:,.2f}"
        )
