FROM python:3.9

WORKDIR /app

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade -r /requirements.txt

COPY . /app

# If running behind a proxy like Nginx or Traefik add --proxy-headers
CMD ["fastapi", "run", "app.py", "--port", "8000", "--proxy-headers"]