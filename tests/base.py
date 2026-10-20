"""Isolamento dos testes em diretórios temporários."""
import tempfile
import unittest
from unittest.mock import patch


class TesteComDados(unittest.TestCase):
    def setUp(self):
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        self.pasta = pasta.name
        ambiente = patch.dict('os.environ', {'PYTU_DATA_DIR': self.pasta})
        ambiente.start()
        self.addCleanup(ambiente.stop)
