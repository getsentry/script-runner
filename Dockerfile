# Stage 1 - build frontend
FROM node:22 AS frontend-build
WORKDIR /frontend

COPY frontend/ /frontend/
RUN npm install
RUN npm run build

# Stage 2 - build and package Python app
FROM python:3.11.7-slim AS build
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
FROM python:3.11.7-slim
WORKDIR /app

# Copy the wheel from the build stage
COPY --from=build /app/dist/*.whl /app/

# Install the wheel
RUN pip install /app/*.whl

# Clean up
RUN rm -rf /app/*.whl

EXPOSE 5000

# Default config for examples
COPY examples/config.yaml /app/config.yaml
ENV CONFIG_FILE_PATH=/app/config.yaml

# Run using the entry point
CMD ["script-runner", "--host", "0.0.0.0", "--port", "5000"]