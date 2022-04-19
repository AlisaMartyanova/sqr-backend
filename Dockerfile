FROM python:3.7-stretch

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py model.py resources.py /app/

EXPOSE 8000

ENTRYPOINT [ "gunicorn", "-b", "0.0.0.0:8000", "app:app"]