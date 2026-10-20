"""Menus e interação com o terminal."""

from datetime import datetime
from collections.abc import Callable
from pytu import anamneses, pacientes, storage

MENU = '''
=====================================
              PyTu
    Sistema de Registro de Anamnese
=====================================

[1] Cadastrar paciente
[2] Listar pacientes
[3] Buscar paciente
[4] Registrar anamnese
[5] Visualizar histórico
[6] Sair
'''


def mostrar_paciente(paciente: dict) -> None:
    """Exibe os dados de um paciente no terminal."""
    print(f"\nID: {paciente['id']}\nNome: {paciente['nome']}")
    print(f"Nascimento: {'/'.join(reversed(paciente['nascimento'].split('-')))}")
    print(f"Sexo: {paciente.get('sexo') or 'Não informado'}")
    print(f"Telefone: {paciente.get('telefone') or 'Não informado'}")


def ler_campo_obrigatorio(pergunta: str, validar: Callable[[str], str]) -> str:
    """Repete a pergunta até que o campo obrigatório seja válido."""
    while True:
        valor = input(pergunta)
        try:
            validar(valor)
        except ValueError as erro:
            print(f'Cadastro não concluído: {erro}')
        else:
            return valor


def cadastrar_paciente() -> None:
    nome = ler_campo_obrigatorio('Nome completo: ', pacientes.validar_nome)
    nascimento = ler_campo_obrigatorio('Nascimento (DD/MM/AAAA): ', pacientes.validar_nascimento)
    paciente = pacientes.cadastrar(
        nome, nascimento, input('Sexo (opcional): '), input('Telefone (opcional): '))
    print(f"Paciente cadastrado. ID: {paciente['id']}")


def listar_pacientes() -> None:
    registros = pacientes.listar()
    if not registros:
        print('Nenhum paciente cadastrado.')
    for paciente in registros:
        mostrar_paciente(paciente)


def buscar_paciente() -> None:
    registros = pacientes.buscar(input('Nome ou ID completo: '))
    if not registros:
        print('Nenhum paciente encontrado.')
    for paciente in registros:
        mostrar_paciente(paciente)


def selecionar_paciente() -> dict:
    """Seleciona pelo ID, que pode ser obtido na listagem ou busca."""
    return pacientes.obter(input('ID completo do paciente (consulte em Listar/Buscar): '))


def registrar_anamnese() -> None:
    paciente = selecionar_paciente()
    print(f"Anamnese de {paciente['nome']} (queixa principal obrigatória).")
    campos = {campo: input(f'{rotulo}: ') for campo, rotulo in anamneses.CAMPOS.items()}
    registro = anamneses.registrar(paciente['id'], **campos)
    print(f"Anamnese registrada. ID: {registro['id']}")


def visualizar_historico() -> None:
    paciente = selecionar_paciente()
    mostrar_paciente(paciente)
    registros = anamneses.historico(paciente['id'])
    if not registros:
        print('Nenhuma anamnese registrada para este paciente.')
    for registro in registros:
        data = datetime.fromisoformat(registro['data_hora']).strftime('%d/%m/%Y %H:%M:%S %z')
        print(f"\n--- Anamnese {registro['id']} | {data} ---")
        for campo, rotulo in anamneses.CAMPOS.items():
            print(f"{rotulo}: {registro[campo] or 'Não informado'}")


def executar() -> None:
    """Mantém o menu ativo e apresenta erros sem expor dados em logs."""
    print('Anamnese simples, direto no terminal.')
    print('Projeto educacional: utilize exclusivamente dados fictícios.')
    acoes = {'1': cadastrar_paciente, '2': listar_pacientes, '3': buscar_paciente,
             '4': registrar_anamnese, '5': visualizar_historico}
    try:
        while True:
            print(MENU)
            opcao = input('Escolha uma opção: ').strip()
            if opcao == '6':
                print('Até logo!')
                return
            if opcao not in acoes:
                print('Opção inválida. Escolha de 1 a 6.')
                continue
            try:
                acoes[opcao]()
            except (ValueError, storage.ErroPersistencia) as erro:
                print(f'Erro: {erro}')
    except (EOFError, KeyboardInterrupt):
        print('\nPrograma encerrado.')
