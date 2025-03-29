# Use the official Python image
FROM python:3.10-slim

# Set environment variables to prevent Python from writing .pyc files and to use unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first (leverage Docker caching for dependencies)
COPY requirements.txt .

# Install Python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    # && pip install psycopg2 \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove --purge -y gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project into the container
COPY . .

# Run the application
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
