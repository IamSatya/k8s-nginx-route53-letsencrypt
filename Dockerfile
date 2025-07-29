FROM python:3.11-slim

WORKDIR /app

COPY operator /app/operator
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "operator.controller"]
