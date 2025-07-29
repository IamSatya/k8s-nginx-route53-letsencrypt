FROM python:3.11-slim

WORKDIR /app

# Install OS-level packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-client \
    curl \
    cron \
    certbot \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy operator code
COPY . .

# Run the Kopf operator
CMD ["python", "run_operator.py"]