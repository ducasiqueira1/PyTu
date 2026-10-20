"""Persistência JSON com substituição atômica e proteção de arquivos inválidos."""

import json
import os
from pathlib import Path
import tempfile


class ErroPersistencia(Exception):
    """Indica que os dados não puderam ser lidos ou gravados com segurança."""


def diretorio_dados() -> Path:
    """Obtém o diretório configurado ou a pasta data do projeto."""
    return Path(os.environ.get('PYTU_DATA_DIR', Path(__file__).resolve().parent.parent / 'data'))


def caminho_arquivo(nome: str) -> Path:
    if nome not in ('pacientes', 'anamneses'):
        raise ValueError('Arquivo de dados desconhecido.')
    return diretorio_dados() / f'{nome}.json'


def ler(nome: str) -> list[dict]:
    """Lê registros; arquivos vazios ou inválidos ficam intactos e bloqueiam escrita."""
    caminho = caminho_arquivo(nome)
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        if not caminho.exists():
            with caminho.open('x', encoding='utf-8') as arquivo:
                arquivo.write('[]\n')
        with caminho.open(encoding='utf-8') as arquivo:
            registros = json.load(arquivo)
        if not isinstance(registros, list) or any(not isinstance(item, dict) for item in registros):
            raise ValueError('Estrutura inválida.')
        return registros
    except (OSError, ValueError) as erro:
        raise ErroPersistencia(
            f'Não foi possível ler {caminho.name}. Preserve o arquivo e restaure uma cópia válida.'
        ) from erro


def gravar(nome: str, registros: list[dict]) -> None:
    """Valida o arquivo existente e substitui seu conteúdo atomicamente."""
    ler(nome)
    caminho = caminho_arquivo(nome)
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=caminho.parent,
                                         prefix=f'.{nome}-', suffix='.tmp', delete=False) as arquivo:
            temporario = Path(arquivo.name)
            json.dump(registros, arquivo, ensure_ascii=False, indent=2)
            arquivo.write('\n')
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, caminho)
    except (OSError, ValueError, TypeError) as erro:
        raise ErroPersistencia(f'Não foi possível gravar {caminho.name}.') from erro
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)
