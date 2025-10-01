# Base image with Python 3.11
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /workspace

# Copy the pyproject.toml and poetry.lock files to the container
COPY ../pyproject.toml ../uv.lock ./

# Copy the rest of the application code into the container
COPY .. /workspace

# Copy the install script into the container
COPY ./docker/install.sh /workspace/install.sh

# Install system dependencies
RUN bash /workspace/install.sh

# Add python path
ENV PYTHONPATH=/workspace:${PYTHONPATH}

# Expose port
EXPOSE 80

# Command to run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "1"]
