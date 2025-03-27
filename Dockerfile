# Stage 1 - build frontend
FROM node:22 AS frontend-build
WORKDIR /frontend

COPY frontend/ /frontend/
RUN npm install
RUN npm run build

# Stage 2 - build and package Python app
FROM python:3.13.2-slim AS build
WORKDIR /app

# Copy and install requirements
COPY pyproject.toml /app/
COPY src/ /app/src/

# Copy frontend build
COPY --from=frontend-build /frontend/dist /app/src/script_runner/frontend/dist

# Build the wheel
RUN pip install build
RUN python -m build --wheel

# Stage 3 - create slim final image
FROM python:3.13.2-slim
WORKDIR /app

# Copy the wheel from the build stage
COPY --from=build /app/dist/*.whl /app/

# Install system dependencies (for clickhouse-driver)
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends build-essential

# Install the wheel and additional requirements
RUN pip install /app/*.whl
RUN pip install -r app/requirements.txt
RUN pip install -r examples/requirements.txt

# Clean up
RUN rm -rf /app/*.whl

EXPOSE 5000

# Configuration
COPY example_config_combined.yaml /app/
ENV FLASK_ENV=production
ENV CONFIG_FILE_PATH=/app/example_config_combined.yaml

# Run using the entry point
CMD ["script-runner", "--host", "0.0.0.0", "--port", "5000"]
