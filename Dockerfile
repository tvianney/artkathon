FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p web_app/uploads web_app/outputs

EXPOSE 5001

WORKDIR /app/web_app

ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

CMD ["python", "app.py"]

