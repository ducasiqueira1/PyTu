"""Cadastro, validação e consulta de pacientes fictícios."""

from datetime import date, datetime
from uuid import uuid4
from pytu import storage


def validar_nome(nome: str) -> str:
    """Valida e normaliza o nome completo."""
    nome = nome.strip()
    if len(nome.split()) < 2:
        raise ValueError('Informe o nome completo (nome e sobrenome).')
    return nome


def validar_nascimento(nascimento: str) -> str:
    """Valida a data informada e retorna sua representação ISO."""
    try:
        data = datetime.strptime(nascimento.strip(), '%d/%m/%Y').date()
    except ValueError as erro:
        raise ValueError('Data de nascimento inválida. Use DD/MM/AAAA.') from erro
    if data > date.today():
        raise ValueError('A data de nascimento não pode estar no futuro.')
    return data.isoformat()


def cadastrar(nome: str, nascimento: str, sexo: str = '', telefone: str = '') -> dict:
    """Cadastra paciente com nome e nascimento no formato DD/MM/AAAA."""
    nome = validar_nome(nome)
    data = validar_nascimento(nascimento)
    registros = listar()
    paciente = {'id': str(uuid4()), 'nome': nome, 'nascimento': data,
                'sexo': sexo.strip(), 'telefone': telefone.strip()}
    registros.append(paciente)
    storage.gravar('pacientes', registros)
    return paciente


def listar() -> list[dict]:
    """Retorna todos os pacientes cadastrados."""
    registros = storage.ler('pacientes')
    for paciente in registros:
        if not all(isinstance(paciente.get(campo), str) and paciente[campo]
                   for campo in ('id', 'nome', 'nascimento')):
            raise storage.ErroPersistencia('Estrutura inválida em pacientes.json; arquivo preservado.')
    return registros


def buscar(termo: str) -> list[dict]:
    """Busca por parte do nome, ignorando maiúsculas, ou por ID exato."""
    termo = termo.strip().casefold()
    if not termo:
        raise ValueError('Informe um nome ou identificador para buscar.')
    return [paciente for paciente in listar()
            if termo in paciente['nome'].casefold() or termo == paciente['id'].casefold()]


def obter(identificador: str) -> dict:
    """Consulta um paciente pelo identificador completo."""
    for paciente in listar():
        if paciente['id'] == identificador.strip():
            return paciente
    raise ValueError('Paciente não encontrado.')
