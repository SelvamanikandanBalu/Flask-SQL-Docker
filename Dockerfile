FROM python:3.15-rc-alpine

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY templates /app/templates/
COPY app.py /app/

CMD ["python", "app.py"]
