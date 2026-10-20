from pytu import pacientes
from tests.base import TesteComDados


class TestePacientes(TesteComDados):
    def test_cadastro_valido(self):
        paciente = pacientes.cadastrar('  Pessoa Fictícia  ', '02/03/2000')
        self.assertEqual(paciente['nome'], 'Pessoa Fictícia')
        self.assertEqual(paciente['nascimento'], '2000-03-02')
        self.assertEqual(paciente['sexo'], '')
        self.assertEqual(pacientes.listar(), [paciente])

    def test_campos_obrigatorios(self):
        for nome, data in [('', '01/01/2000'), ('Pessoa', '01/01/2000'),
                           ('Pessoa Fictícia', ''), ('Pessoa Fictícia', '31/02/2000'),
                           ('Pessoa Fictícia', '01/01/2999')]:
            with self.subTest(nome=nome, data=data), self.assertRaises(ValueError):
                pacientes.cadastrar(nome, data)
        self.assertEqual(pacientes.listar(), [])

    def test_ids_unicos(self):
        ids = {pacientes.cadastrar('Pessoa Fictícia', '01/01/2000')['id'] for _ in range(10)}
        self.assertEqual(len(ids), 10)

    def test_busca(self):
        paciente = pacientes.cadastrar('Pessoa Fictícia', '01/01/2000')
        self.assertEqual(pacientes.buscar('FICTÍCIA'), [paciente])
        self.assertEqual(pacientes.buscar(paciente['id']), [paciente])
        self.assertEqual(pacientes.obter(paciente['id']), paciente)
        self.assertEqual(pacientes.buscar('inexistente'), [])
        with self.assertRaises(ValueError):
            pacientes.buscar(' ')
        with self.assertRaises(ValueError):
            pacientes.obter('inexistente')
