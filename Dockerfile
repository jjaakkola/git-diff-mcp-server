# Use Python slim image
FROM python:3.11-slim

# Install git
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Ensure repo is trusted
RUN git config --global --add safe.directory /repo

# Set working directory
WORKDIR /app

# Set Python unbuffered mode
ENV PYTHONUNBUFFERED=1

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server code
COPY git_diff_server.py .

# Run the server
CMD ["python", "git_diff_server.py"]