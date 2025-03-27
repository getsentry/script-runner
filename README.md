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

