FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ragserver.py .

ENV PYTHONUNBUFFERED=1
# STRICT_PORT=false: in Docker the port is always free, no fail-fast needed
ENV STRICT_PORT=false

EXPOSE 7071

# Start uvicorn directly so it binds to 0.0.0.0 (accessible between containers).
# The lifespan context in ragserver.py (model load + DB connect) runs normally.
CMD ["uvicorn", "ragserver:app", "--host", "0.0.0.0", "--port", "7071"]
