
import unittest

from servicios import ReservaSala
from excepciones import ServicioError


class TestServicios(unittest.TestCase):

    def test_precio_negativo(self):
        with self.assertRaises(ServicioError):
            ReservaSala("Sala inválida", -1000, 5)

    def test_capacidad_invalida(self):
        with self.assertRaises(ServicioError):
            ReservaSala("Sala pequeña", 5000, 0)

    def test_creacion_correcta(self):
        sala = ReservaSala("Sala A", 10000, 10)
        self.assertEqual(sala.capacidad, 10)


if __name__ == "__main__":
    unittest.main()
