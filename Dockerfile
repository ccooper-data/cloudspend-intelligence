FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app
COPY pyproject.toml ./
COPY src/ src/
COPY sql/ sql/
RUN pip install --no-cache-dir --no-deps . && \
    addgroup --system app && adduser --system --ingroup app app

USER app
EXPOSE 8080
CMD ["python", "-m", "cloudspend.api"]
