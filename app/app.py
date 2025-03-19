from flask import Flask, send_from_directory, request, jsonify
import functools
import importlib
from functools import wraps
import requests
from app.utils import load_config, get_module_exports, MainConfig, CombinedConfig, RegionConfig


app = Flask(__name__)

config = load_config()

def cache_static_files(f):
    @wraps(f)
    def add_cache_headers(*args, **kwargs):
        res = f(*args, **kwargs)
        res.headers['Cache-Control'] = 'public, max-age=3600'
        return res
    return add_cache_headers


@functools.lru_cache(maxsize=1)
def get_config():
    assert isinstance(config, (MainConfig, CombinedConfig))

    regions = config.main.regions
    groups = config.groups

    group_data = [
        {
            "group": g,
            "functions": [
                {
                    "name": f.name,
                    "docstring": f.docstring,
                    "source": f.source,
                    "parameters": [
                        {
                            "name": p.name,
                            "default": p.default,
                            "enumValues": p.enumValues
                        }
                        for p in f.parameters
                    ]
                }
                for f in function_group.functions
            ],
        }
        for (g, function_group) in groups.items()
    ]


    return {
        "regions": [r.name for r in regions],
        "groups": group_data,
    }

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


if not isinstance(config, RegionConfig):
    @app.route("/")
    @cache_static_files
    def home():
        return send_from_directory("frontend/dist", "index.html")

    @app.route("/jq.wasm")
    @cache_static_files
    def jq_wasm():
        return send_from_directory("frontend/dist", "jq.wasm")

    @app.route("/assets/<filename>")
    @cache_static_files
    def static_file(filename: str):
        return send_from_directory("frontend/dist/assets", filename)

    @app.route("/run", methods=["POST"])
    def run_all():
        """
        Run a script for all regions
        """
        data = request.get_json()

        results = {}

        group_name = data["group"]
        group = config.groups[group_name]
        requested_function = data["function"]
        function = next((f for f in group.functions if f.name == requested_function), None)
        params = data["parameters"]

        for requested_region in data["regions"]:
            region = next((r for r in config.main.regions if r.name == requested_region), None)
            if region is None:
                return jsonify({"error": "Invalid region"}), 400
            res = requests.post(
                f"{request.scheme}://{region.url}/run_region",
                json={
                    "group": group_name,
                    "function": function.name,
                    "function_checksum": function.checksum,
                    "parameters": params,
                    "region": region.name,
                }
            )

            # TODO: handle errors properly
            assert res.status_code == 200
            results[region.name] = res.json()


        return jsonify(results)

if not isinstance(config, MainConfig):
    @app.route("/run_region", methods=["POST"])
    def run_one_region():
        """
        Run a script for a specific region. This is called from the `/run` endpoint.
        """
        assert isinstance(config, (RegionConfig, CombinedConfig))

        data = request.get_json()
        group_name = data["group"]
        group = config.groups[group_name]
        requested_function = data["function"]

        function = next((f for f in group.functions if f.name == requested_function), None)

        # Do not run the function if it doesn't appear to be the same
        if function.checksum != data["function_checksum"]:
            raise ValueError("Function mismatch")

        params = data["parameters"]
        module = importlib.import_module(group.module)
        func = getattr(module, requested_function)
        group_config = config.region.configs.get(group_name, None)
        return jsonify(func(group_config, *params))


@app.route("/config")
def fetch_config():
    res = get_config()

    # TODO: properly filter based on user access
    res["executableGroups"] = ["example", "kafka", "access_logs"]

    return res


