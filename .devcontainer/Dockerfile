FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Remove Yarn repo (expired GPG key breaks apt-get update in base image)
RUN rm -f /etc/apt/sources.list.d/yarn.list 2>/dev/null || true

# Install system dependencies for document processing
RUN apt-get update && apt-get install -y \
    libreoffice \
    fonts-liberation \
    fonts-dejavu-core \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Set Python environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create workspace directory
WORKDIR /workspace

# Copy requirements first for better caching
COPY requirements.txt requirements-test.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-test.txt

# Create temp directory for file processing with proper ownership
RUN mkdir -p temp && chmod 755 temp && chown vscode:vscode temp

# Install additional development tools
RUN pip install --no-cache-dir \
    black \
    flake8 \
    isort \
    mypy \
    pre-commit

# Copy the rest of the application
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Default command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]