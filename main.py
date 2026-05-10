"""
=============================================================================
MÓDULO: main.py
PROYECTO: Sistema Integral de Gestión - Software FJ
=============================================================================
Punto de entrada principal. Ejecuta 10 operaciones completas que demuestran:
  ✔ Registros válidos e inválidos de clientes
  ✔ Creación correcta e incorrecta de servicios
  ✔ Reservas exitosas y fallidas
  ✔ Confirmación, procesamiento y cancelación de reservas
  ✔ Manejo continuo de excepciones sin detener el sistema
  ✔ Variantes del cálculo de costos (métodos sobrecargados)

El sistema continúa ejecutándose ante cualquier error, registrando cada
incidente en el archivo de logs.
=============================================================================
"""

import os
from datetime import datetime

from gestor import GestorSistema
from servicios import ReservaSala, AlquilerEquipo, AsesoriaTecnica
from excepciones import SoftwareFJError
from logger import logger


def separador(titulo: str):
    """Imprime un separador visual para cada operación en consola."""
    print(f"\n{'▓' * 60}")
    print(f"  {titulo}")
    print(f"{'▓' * 60}")


def main():
    """
    Función principal: ejecuta las 10 operaciones de demostración.
    El sistema continúa ante cualquier error gracias al manejo de excepciones.
    """

    gestor = GestorSistema()

    fecha_log = datetime.now().strftime("%Y%m%d")

    print("\n" + "═" * 60)
    print("   SISTEMA DE GESTIÓN — SOFTWARE FJ")
    print("   Demostración de 10 operaciones completas")
    print("═" * 60)

    # =========================================================================
    # OPERACIÓN 1: Registrar clientes VÁLIDOS
    # =========================================================================
    separador("OP 1 — Registro de clientes válidos")

    c1 = gestor.registrar_cliente("Ana Gómez",    "ana.gomez@empresa.co",  "3001234567", "TechCorp")
    c2 = gestor.registrar_cliente("Carlos Ruiz",  "carlos@mail.com",       "3109876543", "DataSolutions")
    c3 = gestor.registrar_cliente("Lucía Vargas", "lucia@correo.com",      "6012345678", "")

    # =========================================================================
    # OPERACIÓN 2: Intentar registrar clientes INVÁLIDOS
    # =========================================================================
    separador("OP 2 — Registro de clientes inválidos (manejo de errores)")

    print("  → Nombre demasiado corto (mín. 3 caracteres)...")
    r = gestor.registrar_cliente("Li", "li@mail.com", "3001111111")
    print(f"  Resultado: {'Creado' if r else 'Rechazado correctamente ✘'}")

    print("  → Correo sin formato válido (sin @)...")
    r = gestor.registrar_cliente("Pedro Mora", "correo_sin_arroba", "3002222222")
    print(f"  Resultado: {'Creado' if r else 'Rechazado correctamente ✘'}")

    print("  → Teléfono con caracteres inválidos...")
    r = gestor.registrar_cliente("Marta López", "marta@mail.com", "ABCDEFGH")
    print(f"  Resultado: {'Creado' if r else 'Rechazado correctamente ✘'}")

    print("  → Correo duplicado (ya existe ana.gomez@empresa.co)...")
    r = gestor.registrar_cliente("Ana Copia", "ana.gomez@empresa.co", "3003333333")
    print(f"  Resultado: {'Creado' if r else 'Rechazado correctamente ✘'}")

    # =========================================================================
    # OPERACIÓN 3: Crear servicios VÁLIDOS
    # =========================================================================
    separador("OP 3 — Creación de servicios válidos")

    sala_a = ReservaSala(
        nombre="Sala Innovación A",
        precio_hora=80_000,
        capacidad=20,
        tiene_tv=True,
        tiene_wifi=True,
        descripcion="Sala de reuniones con proyector y climatización"
    )
    gestor.agregar_servicio(sala_a)

    sala_b = ReservaSala(
        nombre="Sala Creativa B",
        precio_hora=50_000,
        capacidad=6,
        tiene_tv=False,
        tiene_wifi=True
    )
    gestor.agregar_servicio(sala_b)

    laptops = AlquilerEquipo(
        nombre="Alquiler Laptops Dell",
        precio_hora=25_000,
        tipo_equipo="Laptop Dell Inspiron i7",
        stock=8
    )
    gestor.agregar_servicio(laptops)

    asesoria = AsesoriaTecnica(
        nombre="Asesoría Cloud AWS",
        precio_hora=120_000,
        especialidad="Arquitectura Cloud",
        consultor="Ing. Fernando Jiménez",
        nivel="AVANZADO"
    )
    gestor.agregar_servicio(asesoria)

    asesoria_b = AsesoriaTecnica(
        nombre="Asesoría Python Básica",
        precio_hora=60_000,
        especialidad="Desarrollo de Software",
        consultor="Ing. Sandra Ospina",
        nivel="BASICO"
    )
    gestor.agregar_servicio(asesoria_b)

    gestor.listar_servicios()

    # =========================================================================
    # OPERACIÓN 4: Intentar crear servicios INVÁLIDOS
    # =========================================================================
    separador("OP 4 — Creación de servicios inválidos (manejo de errores)")

    print("  → Precio negativo...")
    try:
        ReservaSala("Sala X", -5_000, 10)
    except SoftwareFJError as e:
        print(f"  Capturado: {e}")

    print("  → Capacidad cero...")
    try:
        ReservaSala("Sala Vacía", 50_000, 0)
    except SoftwareFJError as e:
        print(f"  Capturado: {e}")

    print("  → Equipo sin tipo especificado...")
    try:
        AlquilerEquipo("Equipo sin tipo", 10_000, "")
    except SoftwareFJError as e:
        print(f"  Capturado: {e}")

    print("  → Asesoría con nivel inválido...")
    try:
        AsesoriaTecnica("Asesoría X", 80_000, "IT", "Juan", nivel="EXPERTO")
    except SoftwareFJError as e:
        print(f"  Capturado: {e}")

    # =========================================================================
    # OPERACIÓN 5: Crear y CONFIRMAR reservas exitosas
    # =========================================================================
    separador("OP 5 — Reservas exitosas (creación + confirmación)")

    # Reserva 1: Ana reserva Sala A por 3 horas con 10% de descuento
    r1 = gestor.crear_reserva(c1, sala_a, horas=3, notas="Reunión de lanzamiento")
    if r1:
        print(r1.describir())
        gestor.confirmar_reserva(r1, descuento=0.10)
        print(f"  Estado final: {r1.estado}")

    # Reserva 2: Carlos alquila laptops por 5 horas (sin descuento manual)
    # Nota: AlquilerEquipo.calcular_costo() recibe unidades por su propio método;
    # la confirmación vía gestor calcula sin unidades adicionales (1 unidad).
    r2 = gestor.crear_reserva(c2, laptops, horas=5, notas="Capacitación interna")
    if r2:
        gestor.confirmar_reserva(r2)
        print(f"\n  Costo laptops 5h (1 unidad): ${r2.costo_total:,.2f}")
        print(f"  Estado: {r2.estado}")

    # Reserva 3: Lucía agenda asesoría cloud avanzada por 2 horas con 5% descuento
    r3 = gestor.crear_reserva(c3, asesoria, horas=2, notas="Revisión de arquitectura")
    if r3:
        gestor.confirmar_reserva(r3, descuento=0.05)
        print(f"  Costo asesoría cloud avanzada: ${r3.costo_total:,.2f}")

    # =========================================================================
    # OPERACIÓN 6: Reservas que deben FALLAR
    # =========================================================================
    separador("OP 6 — Reservas inválidas (manejo de errores)")

    print("  → Duración negativa...")
    r_fail = gestor.crear_reserva(c1, sala_b, horas=-2)
    print(f"  Resultado: {'Creada' if r_fail else 'Rechazada correctamente ✘'}")

    print("  → Sin cliente (None)...")
    r_fail = gestor.crear_reserva(None, sala_a, horas=1)
    print(f"  Resultado: {'Creada' if r_fail else 'Rechazada correctamente ✘'}")

    print("  → Servicio suspendido...")
    sala_b.estado = "SUSPENDIDO"
    r_fail = gestor.crear_reserva(c2, sala_b, horas=2)
    print(f"  Resultado: {'Creada' if r_fail else 'Rechazada correctamente ✘'}")
    sala_b.estado = "ACTIVO"   # Restaurar estado

    # =========================================================================
    # OPERACIÓN 7: Operaciones NO PERMITIDAS sobre reservas
    # =========================================================================
    separador("OP 7 — Operaciones no permitidas sobre reservas")

    if r1:
        print(f"  → Confirmar reserva #{r1.id} que ya está {r1.estado}...")
        ok = gestor.confirmar_reserva(r1)
        print(f"  Resultado: {'OK' if ok else 'Rechazado correctamente ✘'}")

    # =========================================================================
    # OPERACIÓN 8: CANCELAR una reserva
    # =========================================================================
    separador("OP 8 — Cancelación de reserva")

    r4 = gestor.crear_reserva(c1, asesoria_b, horas=1, notas="Cancelación planeada")
    if r4:
        print(f"  Reserva #{r4.id} → estado inicial: {r4.estado}")
        gestor.confirmar_reserva(r4)
        print(f"  Reserva #{r4.id} → tras confirmar: {r4.estado}")
        gestor.cancelar_reserva(r4, motivo="Cliente solicitó reprogramación")
        print(f"  Reserva #{r4.id} → tras cancelar: {r4.estado}")

        print(f"  → Cancelar reserva ya CANCELADA (debe fallar)...")
        ok = gestor.cancelar_reserva(r4, "Doble cancelación")
        print(f"  Resultado: {'OK' if ok else 'Rechazado correctamente ✘'}")

    # =========================================================================
    # OPERACIÓN 9: PROCESAR (completar) reservas confirmadas
    # =========================================================================
    separador("OP 9 — Procesamiento de reservas confirmadas")

    if r2:
        print(f"  Procesando reserva #{r2.id} (laptops)...")
        gestor.procesar_reserva(r2)

    if r3:
        print(f"  Procesando reserva #{r3.id} (asesoría cloud)...")
        gestor.procesar_reserva(r3)

    # Intentar procesar una reserva PENDIENTE (sin confirmar) → debe fallar
    r5 = gestor.crear_reserva(c3, sala_a, horas=4, notas="Test: proceso sin confirmar")
    if r5:
        print(f"  → Procesar reserva #{r5.id} sin confirmar (debe fallar)...")
        ok = gestor.procesar_reserva(r5)
        print(f"  Resultado: {'OK' if ok else 'Rechazado correctamente ✘'}")

    # =========================================================================
    # OPERACIÓN 10: Variantes del cálculo de costos (métodos sobrecargados)
    # =========================================================================
    separador("OP 10 — Variantes de cálculo de costos (métodos sobrecargados)")

    print("  Sala Innovación A — $80,000/hora | Capacidad: 20 personas\n")

    # Variante 1: Solo horas, con IVA 19% (default)
    v1 = sala_a.calcular_costo(horas=2)
    print(f"  V1 — 2h, sin descuento, con IVA 19%        : ${v1:>14,.2f}")

    # Variante 2: Con descuento 15%, con IVA
    v2 = sala_a.calcular_costo(horas=2, descuento=0.15)
    print(f"  V2 — 2h, 15% descuento, con IVA            : ${v2:>14,.2f}")

    # Variante 3: Con descuento 15%, sin IVA (cliente exento)
    v3 = sala_a.calcular_costo(horas=2, descuento=0.15, aplicar_impuesto=False)
    print(f"  V3 — 2h, 15% descuento, sin IVA            : ${v3:>14,.2f}")

    # Variante 4: Grupo grande (15 personas → recargo +15%)
    v4 = sala_a.calcular_costo(horas=2, personas=15)
    print(f"  V4 — 2h, 15 personas (recargo 15%), con IVA: ${v4:>14,.2f}")

    # Variante asesoría: nivel del servicio vs. nivel override
    print()
    va1 = asesoria.calcular_costo(horas=3)
    va2 = asesoria.calcular_costo(horas=3, nivel_override="INTERMEDIO")
    print(f"  Asesoría Cloud 3h — nivel AVANZADO          : ${va1:>14,.2f}")
    print(f"  Asesoría Cloud 3h — nivel INTERMEDIO        : ${va2:>14,.2f}")

    # Variante alquiler: múltiples unidades con descuento por volumen
    print()
    va3 = laptops.calcular_costo(horas=5, unidades=4)   # 4 unidades → descuento 10%
    print(f"  Laptops 5h — 4 unidades (descuento vol. 10%): ${va3:>14,.2f}")

    # Error de cálculo: descuento mayor a 1.0 → debe ser capturado
    print("\n  → Descuento inválido (> 100%)...")
    try:
        sala_a.calcular_costo(horas=2, descuento=1.5)
    except SoftwareFJError as e:
        print(f"  Capturado correctamente: {e}")

    # =========================================================================
    # LISTADOS Y REPORTE FINAL
    # =========================================================================
    gestor.listar_clientes()
    gestor.listar_reservas()
    gestor.reporte_general()

    archivo_log = f"logs/software_fj_{fecha_log}.log"
    print(f"  Archivo de logs: {archivo_log}")
    print("  Sistema finalizado exitosamente.\n")
    logger.info("Sistema Software FJ — Ejecución finalizada correctamente.")


# ── Punto de entrada ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
