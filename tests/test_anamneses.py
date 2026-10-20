from datetime import datetime
from pytu import anamneses, pacientes, storage
from tests.base import TesteComDados


class TesteAnamneses(TesteComDados):
    def setUp(self):
        super().setUp()
        self.paciente = pacientes.cadastrar('Pessoa Fictícia', '01/01/2000')

    def test_registro_completo(self):
        campos = {campo: 'Texto fictício' for campo in anamneses.CAMPOS}
        registro = anamneses.registrar(self.paciente['id'], **campos)
        self.assertEqual(registro['paciente_id'], self.paciente['id'])
        self.assertIsNotNone(datetime.fromisoformat(registro['data_hora']).tzinfo)
        for campo in campos:
            self.assertEqual(registro[campo], campos[campo])

    def test_associacao_e_ids(self):
        outro = pacientes.cadastrar('Outra Pessoa', '01/01/1990')
        primeiro = anamneses.registrar(self.paciente['id'], queixa_principal='Exemplo A')
        segundo = anamneses.registrar(outro['id'], queixa_principal='Exemplo B')
        self.assertNotEqual(primeiro['id'], segundo['id'])
        self.assertEqual(anamneses.historico(self.paciente['id']), [primeiro])
        self.assertEqual(anamneses.historico(outro['id']), [segundo])

    def test_historico_cronologico(self):
        antigo = anamneses.registrar(self.paciente['id'], queixa_principal='Exemplo A')
        novo = anamneses.registrar(self.paciente['id'], queixa_principal='Exemplo B')
        antigo['data_hora'] = '2020-01-01T10:00:00+00:00'
        novo['data_hora'] = '2021-01-01T10:00:00+00:00'
        storage.gravar('anamneses', [novo, antigo])
        self.assertEqual(anamneses.historico(self.paciente['id']), [antigo, novo])

    def test_validacoes(self):
        self.assertEqual(anamneses.historico(self.paciente['id']), [])
        with self.assertRaises(ValueError):
            anamneses.registrar('inexistente', queixa_principal='Exemplo')
        with self.assertRaises(ValueError):
            anamneses.registrar(self.paciente['id'], queixa_principal=' ')
        with self.assertRaises(ValueError):
            anamneses.registrar(self.paciente['id'], desconhecido='Exemplo')
        self.assertEqual(anamneses.listar(), [])
