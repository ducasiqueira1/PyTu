# Imagem oficial: Python e biblioteca padrão, sem pacotes adicionais.
FROM python:3.12-slim

WORKDIR /app

# Saída imediata no terminal e diretório configurável de persistência.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTU_DATA_DIR=/app/data

# Apenas o código necessário à execução entra na imagem.
COPY main.py ./
COPY pytu/ ./pytu/
RUN mkdir -p /app/data

# Use docker run -it para interagir; monte um volume para manter os dados.
CMD ["python", "main.py"]
