FROM python:3.11-slim

WORKDIR /app

COPY ../shared /shared
RUN pip install -e /shared

COPY . /app
RUN pip install -e .

EXPOSE 8000
CMD ["uvicorn", "dualdoc_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
