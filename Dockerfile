FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \ PYTHONUNBUFFERED=1 \ PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN python -m pip install --upgrade pip 

COPY requirements.txt /app/

RUN pip install -r requirements.txt 

COPY app ./app

EXPOSE 8000 

CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000","--reload"]
