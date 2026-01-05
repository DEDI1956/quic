# Dockerfile for VPN Telegram Bot
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    nginx \
    certbot \
    && rm -rf /var/lib/apt/lists/*

# Install Xray-core
RUN bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p /app/backups /app/reports /app/logs /app/qrcodes

# Make scripts executable
RUN chmod +x manage.py cron_tasks.py

# Expose ports
EXPOSE 80 443 8080 8443 445 8081

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Initialize database
RUN python3 -c "from database import init_db; init_db()"

# Start bot
CMD ["python3", "bot.py"]
