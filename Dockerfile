FROM python:3.11-slim

WORKDIR /test_aiogram

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY .env .env

CMD ["python", "main.py"]