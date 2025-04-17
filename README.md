# script-runner

Run Python scripts on production data.

This application can run in either combined or multi-region mode.

For multi-region mode, set `mode: region` for region, and `mode: main` for the main deployment. `mode: combined` runs both together.

## Example data:

- These are in the examples/scripts directory
- You can generate data for the examples via `make generate-example-data`

## Configuration

Runs in `combined`, `main` and `region` mode. Combined is mostly for dev and testing.

check `config.schema.json`

## Development Setup

To run the application locally for development, you need to start both the backend (Flask) and frontend (Vite) servers in separate terminals.

**1. Start the Backend Server:**

- Navigate to the project root directory (`script-runner`).
- Activate the Python virtual environment (e.g., `source .venv/bin/activate`).
- Set the configuration file path environment variable (replace with your actual config file):
  ```bash
  export CONFIG_FILE_PATH="example_config_main.yaml"
  ```
- Run the Flask development server:
  ```bash
  flask --app script_runner.app run
  ```
- The backend should now be running (typically on `http://127.0.0.1:5000`).

**2. Start the Frontend Server:**

- Open a **separate** terminal.
- Navigate to the frontend directory:
  ```bash
  cd script_runner/frontend
  ```
- Install dependencies if you haven't already:
  ```bash
  npm install
  ```
- Run the Vite development server:
  ```bash
  npm run dev
  ```
- The frontend should now be running (typically on `http://localhost:5173`) and will automatically proxy API requests to the backend thanks to the proxy configured in `vite.config.ts`.

**Accessing the App:**

Open your browser and navigate to the frontend URL (e.g., `http://localhost:5173`).

**Stopping the Servers:**

Press `Ctrl + C` in each terminal window.

**(Optional) Using Make:**

This project may contain a `Makefile` with a command to simplify this process (e.g., `make devserver`). Check the `Makefile` content; if available, this command might start both servers for you.
