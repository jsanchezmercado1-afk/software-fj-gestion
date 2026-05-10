
import json
from pathlib import Path

class PersistenciaJSON:
    """
    Clase encargada de guardar y cargar información del sistema
    utilizando archivos JSON.
    """

    ARCHIVO = "datos_sistema.json"

    @staticmethod
    def guardar_clientes(clientes):
        datos = []

        for cliente in clientes:
            datos.append({
                "nombre": cliente.nombre,
                "correo": cliente.correo,
                "telefono": cliente.telefono
            })

        with open(PersistenciaJSON.ARCHIVO, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

    @staticmethod
    def cargar_clientes():
        ruta = Path(PersistenciaJSON.ARCHIVO)

        if not ruta.exists():
            return []

        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
