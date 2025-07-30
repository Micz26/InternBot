FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY .env .

COPY ./src ./src

RUN pip install --no-cache-dir -e .

# Uruchom aplikację
CMD ["uvicorn", "intern_bot.api.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
