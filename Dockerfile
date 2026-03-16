FROM python:3.12-slim-bookworm

WORKDIR /code

# RUN python -m venv venv
# ENV PATH="venv/bin:$PATH"
# Default for standalone runs; override in deployment (e.g. GOTENBERG_API_URL=http://gotenberg.web:3000 for Swarm)
ENV GOTENBERG_API_URL=http://host.docker.internal:3000

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-warn-script-location \
    --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
