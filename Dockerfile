FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create database directory and copy pre-built database
RUN mkdir -p /app/data
COPY instance/paleo_bible.db /app/data/paleo_bible.db

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV DATABASE_URL=sqlite:///data/paleo_bible.db

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]