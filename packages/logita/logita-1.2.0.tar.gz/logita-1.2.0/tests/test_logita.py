import unittest
from logita import Logita  # Ajusta el nombre del módulo si es distinto

class TestLogita(unittest.TestCase):

    def setUp(self):
        self.log = Logita()

    def test_debug(self):
        self.log.debug("Mensaje debug sin salto de línea...", line=False)
        self.log.debug(" continuación en la misma línea.")
        print()  # salto manual para legibilidad

    def test_info(self):
        self.log.info("Mensaje info con salto de línea")

    def test_success(self):
        self.log.success("Mensaje success con salto de línea")

    def test_warning(self):
        self.log.warning("Mensaje warning con salto de línea")

    def test_error(self):
        self.log.error("Mensaje error con salto de línea")

    def test_critical(self):
        self.log.critical("Mensaje critical con salto de línea")

    def test_exception(self):
        self.log.exception("Mensaje exception con salto de línea")

if __name__ == '__main__':
    unittest.main()
