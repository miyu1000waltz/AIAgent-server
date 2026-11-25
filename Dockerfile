FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ .

EXPOSE 8200

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8200"]
