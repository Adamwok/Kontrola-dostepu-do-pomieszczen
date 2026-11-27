FROM python:3.15-slim
WORKDIR /app
ENV PYTHONPATH=/app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN useradd --create-home app
COPY --chown=app:app ./src ./src
COPY --chown=app:app ./tests ./tests
USER app
EXPOSE 8080
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--root-path", "/api"]