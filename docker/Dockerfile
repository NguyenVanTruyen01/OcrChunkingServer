FROM python:3.11-slim

WORKDIR /workspace

# Copy từ root vào container
COPY pyproject.toml uv.lock ./
COPY . /workspace

COPY docker/install.sh /workspace/install.sh

RUN bash /workspace/install.sh

ENV PYTHONPATH=/workspace:${PYTHONPATH}

EXPOSE 80
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "1"]
