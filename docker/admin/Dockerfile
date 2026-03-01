FROM python:3.12-alpine

WORKDIR /app

RUN pip install --no-cache-dir flask

COPY site-admin.app.py /app/app.py
COPY site-admin.admin.html /app/admin.html

EXPOSE 5005

CMD ["python", "/app/app.py"]
