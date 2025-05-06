# script-runner

A tool for defining python functions, triggering their execution and displaying results via a user interface.

Used at Sentry to allow specific users to run predefined Python scripts on production data.


## Deployment modes

Multi-region deployments enable aggregating results across multiple "regions" or "silos", whilst still enabling script execution to be performed in a single region.
- set `mode: main` for the central region
- set `mode: region` for each instance of the application deployed in each regions


For a single deployment in one region use `mode:combined`. Currently we only use this for dev and testing.


## Writing custom scripts
Scripts are standard python functions organized into groups.

All of the arguments to a function must be annotated with one of the supported parameter types. Currently there are 5.

- Text
- Textarea
- Integer
- Number
- Select

Example:
```python
def print_value(input: Text) -> None:
    """
    for short text, renders <input type="text" /> in the ui
    """
    print(input.value)

def print_long_value(input: TextArea) -> None:
    """
    multiline text, renders <textarea /> in the ui
    """
    print(input.value)
```

The annotation controls how the element is displayed in the UI, and the Python type of the value (`str`, `int` or `float`)

The return value of the function can be anything, as long as it is json serializable

Any functions exported by a module via `__all__` will be picked up automatically and displayed in the UI.


## Writing tests
Use the `execute_with_context` helper from the testutils module to call your function with mock values.


## Authentication
currently google iap (and no auth) are supported

for google iap, set the `audience_code` as well as `iap_principals` (group -> iap principal mapping) in the config


## Example data:
- These are in the examples/scripts directory

## Configuration
check `config.schema.json` for configuration format and required fields.
there is also an example of each mode in this repository: `example_config_combined.yaml`, `example_config_main.yaml`, `example_config_local.yaml`

## Development

- Run `make develop`. The application will run on combined mode on `http://127.0.0.1:5000`

- If you want UI hot reloading, you have to run the vite server separately.
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
- The frontend should now be running on `http://localhost:5173` and will automatically proxy API requests to the backend thanks to the proxy configured in `vite.config.ts`.
