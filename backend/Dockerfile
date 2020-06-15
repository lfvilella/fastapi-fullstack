FROM python:3.7
EXPOSE 8000
WORKDIR /app
COPY requirements* /app/backend/
RUN pip install --upgrade pip && pip install -r backend/requirements-dev.txt
CMD ["uvicorn", "backend.app.api:app", "--host 0.0.0.0"]