FROM python:3.11-slim

WORKDIR /app

# Install required packages
RUN apt-get update && \
    apt-get install -y openssl python3-dev gcc && \
    pip install flask requests netifaces && \
    apt-get remove -y python3-dev gcc && \
    apt-get autoremove -y && \
    apt-get clean

# Generate self-signed certificate
RUN openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=192.168.1.3"

# Copy application files
COPY app.py .
COPY static static/

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"] 