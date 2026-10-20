# PyTu

**Sistema de Registro de Anamnese em Python**  
Anamnese simples, direto no terminal.

Projeto educacional pequeno para estudar Python, funções, módulos, JSON, testes,
Git e Docker. Utilize **somente dados fictícios**. O PyTu não é um prontuário
adequado ao uso assistencial real: não possui autenticação, criptografia nem
controles de acesso.

## Funcionalidades

- Cadastro de pacientes com UUID, nome completo e nascimento obrigatórios;
  sexo e telefone opcionais.
- Listagem e busca por parte do nome (sem distinguir maiúsculas) ou ID completo.
- Múltiplas anamneses por paciente, com UUID e data/hora com fuso automático.
- Oito campos de anamnese: queixa principal (obrigatória), HDA, antecedentes
  pessoais e familiares, medicamentos, alergias, hábitos e observações.
- Histórico do mais antigo ao mais recente e persistência local em JSON UTF-8.

## Estrutura

```text
.
├── .gitignore
├── .dockerignore
├── Dockerfile
├── README.md
├── main.py
├── pytu/
│   ├── __init__.py
│   ├── cli.py
│   ├── pacientes.py
│   ├── anamneses.py
│   └── storage.py
├── tests/
│   ├── __init__.py
│   ├── base.py
│   ├── test_pacientes.py
│   ├── test_anamneses.py
│   ├── test_storage.py
│   └── test_cli.py
└── data/
    └── .gitkeep
```

`main.py` inicia o menu; `cli.py` cuida da interação; pacientes e anamneses
concentram as regras; `storage.py` lê e grava os arquivos.

## Execução com Python

Requer Python **3.12 ou superior**. Não é necessário instalar pacotes.
Na raiz do projeto:

```bash
python --version
python main.py
```

Em sistemas que disponibilizam o interpretador como `python3`, utilize:

```bash
python3 --version
python3 main.py
```

Escolha uma opção de 1 a 6. Informe nascimento em `DD/MM/AAAA`, por exemplo
`01/01/2000`. Um exemplo de nome fictício é `Pessoa Fictícia`. O ID gerado é
exibido ao cadastrar; use a busca ou listagem para copiá-lo ao registrar uma
anamnese ou consultar o histórico. Datas futuras e datas inexistentes são
rejeitadas. Se o nome ou a data forem inválidos, o cadastro pede a correção
do campo antes de continuar. O registro só é confirmado pela mensagem
`Paciente cadastrado. ID: ...`. Campos opcionais podem ficar em branco. A opção 6 encerra; Ctrl+C
ou fim da entrada também encerram o programa.

Por padrão, os arquivos `pacientes.json` e `anamneses.json` são criados na pasta
`data/` do projeto conforme utilizados. Para escolher outro diretório:

```bash
PYTU_DATA_DIR=/tmp/pytu-aula python3 main.py
```

Os dados persistem entre execuções. Os testes usam diretórios temporários.
Arquivos de dados são ignorados pelo Git e excluídos da imagem Docker.

## Docker: imagem, contêiner e volume

Requer Docker instalado, daemon ativo e permissão para acessá-lo.
A **imagem** é o pacote de Python e código construído pelo Dockerfile;
o **contêiner** é uma execução isolada dessa imagem. Um **volume** mantém os
arquivos fora do ciclo de vida do contêiner.

Construa a imagem oficial baseada em `python:3.12-slim`:

```bash
docker build -t pytu .
```

A construção inicial pode precisar de internet para baixar a imagem Python.
O programa não precisa de internet para funcionar.

Execute com terminal interativo (`-i` mantém entrada aberta e `-t` aloca terminal):

```bash
docker run --rm -it pytu
```

Sem volume, os dados ficam na camada gravável do contêiner. Com `--rm`, essa
camada é removida ao encerrar; portanto, os dados dessa execução são perdidos.

Para manter dados entre contêineres, utilize um volume nomeado:

```bash
docker run --rm -it \
  -v pytu-data:/app/data \
  pytu
```

O Docker cria `pytu-data` se necessário. Execute novamente o mesmo comando para
consultar os registros anteriores. A remoção do contêiner com `--rm` mantém o
volume. Para inspecioná-lo:

```bash
docker volume ls
docker volume inspect pytu-data
```

Dentro da imagem, `PYTU_DATA_DIR` tem valor padrão `/app/data`. Para alterá-lo,
ajuste também o ponto de montagem:

```bash
docker run --rm -it \
  -e PYTU_DATA_DIR=/registros \
  -v pytu-data:/registros \
  pytu
```

Para verificar a persistência: cadastre uma pessoa fictícia, saia pela opção 6,
execute novamente com o mesmo volume e escolha listar pacientes. Sem volume,
um novo contêiner começa sem os registros da execução anterior.

## Testes

Na raiz do projeto:

```bash
python -m unittest discover -s tests -v
```

Ou `python3 -m unittest discover -s tests -v`, conforme o ambiente.
São 18 testes: cadastro, validações, UUIDs, buscas, associação de anamneses,
ordenação do histórico, UTF-8, reinicialização em outro processo, arquivos
inválidos, falha de substituição atômica e fluxo do menu.

Validação no ambiente de desenvolvimento: **18 testes aprovados no Python
3.13.5**. O build Docker foi tentado, mas o daemon recusou acesso ao socket
(`/var/run/docker.sock`: permission denied). Assim, a construção da imagem,
a execução no Python 3.12 do contêiner e a persistência por volume **não foram
validadas neste ambiente**.

## Git

O desenvolvimento foi registrado em commits por etapa. Comandos principais:

```bash
git init
git status
python3 -m unittest discover -s tests -v
git add pytu/pacientes.py
git commit -m "feat: implementa cadastro e busca de pacientes"
git log --oneline
```

Antes de cada commit, confira o estado e execute a verificação pertinente.
Adicione explicitamente apenas os arquivos da etapa. Não versione dados de
pacientes ou arquivos temporários. Não é necessário publicar em um remoto
para estudar o histórico local.

## Persistência e limitações

A gravação usa um arquivo temporário no mesmo diretório, sincroniza seu conteúdo
e o substitui com `os.replace`. Se o JSON estiver vazio, ilegível ou inválido,
o sistema informa o problema e bloqueia a operação, preservando o arquivo.
Mantenha uma cópia antes de reparar manualmente ou restaurar um backup válido.
Arquivos inválidos nunca são automaticamente apagados ou reinicializados.

- Uso educacional, exclusivamente com dados fictícios; sem autenticação,
  criptografia, controle de acesso ou trilha de auditoria.
- Uma instância por diretório de dados: não há bloqueio entre processos;
  execuções simultâneas podem sobrescrever atualizações. A substituição atômica
  evita arquivos parcialmente gravados, mas não resolve concorrência.
- Arquivos JSON são carregados integralmente em memória, adequados a pequenos
  conjuntos de registros.
- Sem edição, exclusão, exportação ou backup automático, fora do escopo.
- Data/hora utiliza o fuso do sistema/contêiner, que pode diferir do computador
  hospedeiro; o deslocamento é armazenado junto ao registro.
