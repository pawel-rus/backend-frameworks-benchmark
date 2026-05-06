# Use a lightweight Debian-based image with standard glibc
FROM python:3.11-slim-bookworm

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

# Run the Uvicorn server with a single worker
# (Since we limit the container to 1 vCPU, 1 worker is the fairest configuration)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--workers", "1"]