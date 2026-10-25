FROM python:3.15-slim
WORKDIR /app/src
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN useradd --create-home app
USER app
COPY ./src ./src
EXPOSE 8080
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]