# Use official Python image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Install MySQL client dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose the port Django runs on
EXPOSE 8000

# Run the Django development server
CMD ["sh", "-c", "USE_SQLITE=1 python manage.py migrate && USE_SQLITE=1 python manage.py runserver 0.0.0.0:8000"]