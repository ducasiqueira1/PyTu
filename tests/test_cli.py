from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch
from pytu import cli, pacientes, anamneses
from tests.base import TesteComDados


class TesteCli(TesteComDados):
    def test_fluxo_completo(self):
        paciente = pacientes.cadastrar('Pessoa Fictícia', '01/01/2000')
        entradas = ['0', '1', 'Outra Pessoa', '02/02/2000', '', '',
                    '2', '3', 'fictícia', '4', paciente['id'],
                    *['Exemplo fictício'] * 8, '5', paciente['id'], '6']
        saida = StringIO()
        with patch('builtins.input', side_effect=entradas), redirect_stdout(saida):
            cli.executar()
        self.assertIn('Opção inválida', saida.getvalue())
        self.assertIn('Anamnese registrada', saida.getvalue())
        self.assertIn('História da doença atual', saida.getvalue())
        self.assertEqual(len(pacientes.listar()), 2)
        self.assertEqual(len(anamneses.historico(paciente['id'])), 1)

    def test_erro_nao_encerra_menu(self):
        with patch('builtins.input', side_effect=['5', 'inexistente', '6']), redirect_stdout(StringIO()) as saida:
            cli.executar()
        self.assertIn('Paciente não encontrado', saida.getvalue())
        self.assertIn('Até logo', saida.getvalue())

    def test_fim_da_entrada(self):
        with patch('builtins.input', side_effect=EOFError), redirect_stdout(StringIO()) as saida:
            cli.executar()
        self.assertIn('Programa encerrado', saida.getvalue())

    def test_corrigir_campos_e_listar_paciente(self):
        entradas = ['1', '', 'Pessoa', 'Pessoa Fictícia', '', '31/02/2000',
                    '01/01/2000', '', '', '2', '6']
        saida = StringIO()
        with patch('builtins.input', side_effect=entradas), redirect_stdout(saida):
            cli.executar()
        texto = saida.getvalue()
        self.assertEqual(texto.count('Cadastro não concluído:'), 4)
        self.assertIn('Paciente cadastrado. ID:', texto)
        self.assertIn('Nome: Pessoa Fictícia', texto)
        self.assertNotIn('Nenhum paciente cadastrado.', texto)
        self.assertEqual(len(pacientes.listar()), 1)
