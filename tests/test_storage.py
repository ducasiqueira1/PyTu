import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch
from pytu import storage, pacientes
from tests.base import TesteComDados


class TesteStorage(TesteComDados):
    def test_criacao_e_utf8(self):
        self.assertEqual(storage.ler('pacientes'), [])
        storage.gravar('pacientes', [{'nome': 'Pessoa Fictícia'}])
        caminho = Path(self.pasta) / 'pacientes.json'
        self.assertIn('Fictícia', caminho.read_text(encoding='utf-8'))
        self.assertEqual(json.loads(caminho.read_text()), [{'nome': 'Pessoa Fictícia'}])

    def test_reinicio_em_outro_processo(self):
        paciente = pacientes.cadastrar('Pessoa Fictícia', '01/01/2000')
        resultado = subprocess.run(
            [sys.executable, '-c', 'import json; from pytu import pacientes; print(json.dumps(pacientes.listar()))'],
            capture_output=True, text=True, check=True, env=os.environ.copy())
        self.assertEqual(json.loads(resultado.stdout), [paciente])

    def test_invalidos_preservados(self):
        caminho = Path(self.pasta) / 'pacientes.json'
        for conteudo in ('', '{invalido', '{}', '[1]', '\ufffd'):
            with self.subTest(conteudo=conteudo):
                caminho.write_text(conteudo, encoding='utf-8')
                with self.assertRaises(storage.ErroPersistencia):
                    storage.ler('pacientes')
                with self.assertRaises(storage.ErroPersistencia):
                    storage.gravar('pacientes', [])
                self.assertEqual(caminho.read_text(encoding='utf-8'), conteudo)

    def test_bytes_invalidos_preservados(self):
        caminho = Path(self.pasta) / 'pacientes.json'
        caminho.write_bytes(b'\xff')
        with self.assertRaises(storage.ErroPersistencia):
            storage.ler('pacientes')
        self.assertEqual(caminho.read_bytes(), b'\xff')

    def test_falha_atomica_preserva_dados(self):
        storage.gravar('pacientes', [{'id': 'ficticio'}])
        with patch('pytu.storage.os.replace', side_effect=OSError('Falha simulada')):
            with self.assertRaises(storage.ErroPersistencia):
                storage.gravar('pacientes', [])
        self.assertEqual(storage.ler('pacientes'), [{'id': 'ficticio'}])
        self.assertEqual(list(Path(self.pasta).glob('*.tmp')), [])

    def test_estrutura_de_paciente_invalida(self):
        storage.gravar('pacientes', [{}])
        with self.assertRaises(storage.ErroPersistencia):
            pacientes.cadastrar('Pessoa Fictícia', '01/01/2000')
        self.assertEqual(storage.ler('pacientes'), [{}])
