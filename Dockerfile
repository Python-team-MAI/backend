# FROM python:3.12-slim

# WORKDIR /app

# COPY requirements.txt .

# RUN pip install --no-cache-dir --upgrade pip && \
#     pip install --no-cache-dir -r requirements.txt

# COPY . .
FROM python:3.12.6

WORKDIR /app

COPY requirements.txt ./

COPY . .

RUN pip install -r requirements.txt


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]