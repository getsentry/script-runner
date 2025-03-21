# Stage 1 - build frontend
FROM node:22 AS frontend-build
WORKDIR /frontend

COPY app/frontend/ /frontend/
RUN npm install
RUN npm run build

# Stage 2 - copy files, build and serve python app
FROM python:3.13.2-slim
WORKDIR /app
COPY --from=frontend-build /frontend/dist /app/app/frontend/dist

COPY requirements.txt /app/app/
COPY app/*.py app/*.json /app/app/
COPY example_config_combined.yaml /app/

COPY examples/scripts/ /app/examples/scripts/
COPY examples/requirements.txt /app/examples/

# For clickhouse-driver, remove once scripts are split into separate repo
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends build-essential

RUN pip install -r app/requirements.txt
RUN pip install -r examples/requirements.txt

EXPOSE 5000

ENV FLASK_ENV=production
ENV CONFIG_FILE_PATH=/app/example_config_combined.yaml

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app.app:app"]
