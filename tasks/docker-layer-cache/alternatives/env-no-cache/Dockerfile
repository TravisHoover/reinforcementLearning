FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY --chown=root:root requirements.txt /app/
RUN pip install --requirement requirements.txt
COPY . .

CMD ["python", "-m", "app"]
