import argparse
import os
import sys
from script_runner.app import create_app


def main():
    parser = argparse.ArgumentParser(
        description="Run the Script Runner web application."
    )
    parser.add_argument(
        "--config",
        dest="config_path",
        help="Path to the configuration file.",
        default=os.getenv("CONFIG_FILE_PATH"),
    )
    parser.add_argument(
        "--host", dest="host", help="Host to bind to.", default="127.0.0.1"
    )
    parser.add_argument(
        "--port", dest="port", help="Port to bind to.", default=5000, type=int
    )
    parser.add_argument(
        "--debug", dest="debug", help="Run in debug mode.", action="store_true"
    )

    args = parser.parse_args()

    if not args.config_path:
        print(
            "Error: Config file path not specified. Use --config or set CONFIG_FILE_PATH environment variable."
        )
        sys.exit(1)

    app = create_app(args.config_path)
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
