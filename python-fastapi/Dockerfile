# Use a lightweight Debian-based image with standard glibc
FROM python:3.11-slim-bookworm

# Set environment variables to optimize Python for Docker
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first (Docker layer caching optimization)
COPY requirements.txt .

# Install dependencies without saving cache to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY main.py .

# Expose the port the app runs on
EXPOSE 3000

# Run the Uvicorn server with 2 workers to leverage both CPU cores and no access log
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--workers", "2", "--no-access-log"]