"""Registro de anamneses e histórico cronológico por paciente."""

from datetime import datetime
from uuid import uuid4
from pytu import pacientes, storage

CAMPOS = {
    'queixa_principal': 'Queixa principal',
    'hda': 'História da doença atual (HDA)',
    'antecedentes_pessoais': 'Antecedentes pessoais',
    'antecedentes_familiares': 'Antecedentes familiares',
    'medicamentos': 'Medicamentos em uso',
    'alergias': 'Alergias',
    'habitos': 'Hábitos de vida',
    'observacoes': 'Observações adicionais',
}


def listar() -> list[dict]:
    """Lê anamneses e verifica os campos necessários ao histórico."""
    registros = storage.ler('anamneses')
    for registro in registros:
        if not all(isinstance(registro.get(campo), str) for campo in
                   ('id', 'paciente_id', 'data_hora', *CAMPOS)):
            raise storage.ErroPersistencia('Estrutura inválida em anamneses.json; arquivo preservado.')
        try:
            data = datetime.fromisoformat(registro['data_hora'])
            if data.tzinfo is None:
                raise ValueError('Data sem fuso horário.')
        except ValueError as erro:
            raise storage.ErroPersistencia('Data inválida em anamneses.json; arquivo preservado.') from erro
    return registros


def registrar(paciente_id: str, **campos: str) -> dict:
    """Registra os oito campos, exigindo a queixa principal."""
    paciente = pacientes.obter(paciente_id)
    if set(campos) - set(CAMPOS):
        raise ValueError('Campo de anamnese desconhecido.')
    dados = {campo: campos.get(campo, '').strip() for campo in CAMPOS}
    if not dados['queixa_principal']:
        raise ValueError('A queixa principal é obrigatória.')
    registros = listar()
    registro = {'id': str(uuid4()), 'paciente_id': paciente['id'],
                'data_hora': datetime.now().astimezone().isoformat(timespec='seconds'), **dados}
    registros.append(registro)
    storage.gravar('anamneses', registros)
    return registro


def historico(paciente_id: str) -> list[dict]:
    """Retorna os registros do paciente do mais antigo ao mais recente."""
    paciente = pacientes.obter(paciente_id)
    return sorted((registro for registro in listar() if registro['paciente_id'] == paciente['id']),
                  key=lambda registro: datetime.fromisoformat(registro['data_hora']))
