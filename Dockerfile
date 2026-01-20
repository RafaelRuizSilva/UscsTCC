# Dockerfile
FROM python:3.11-slim

WORKDIR UscsTCC

COPY requirements.txt requirements.txt

# Instalações com verificação e sem cache
RUN pip install --upgrade pip \
 && pip uninstall -y jwt || true \
 && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
