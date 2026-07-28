FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/ai-db
RUN mkdir -p /app/upload_document

EXPOSE 8000

CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8000"]