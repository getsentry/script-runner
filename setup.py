import os
import subprocess
import sys
from pathlib import Path

from setuptools import setup
from distutils.command.build import build


project_root = Path(__file__).parent.resolve()
frontend_dir = project_root / "script_runner" / "frontend"


class FrontendBuild(build):
    """Custom build command to build the frontend assets."""

    def run(self):
        # Build the frontend assets using npm
        print(f"Project Root: {project_root}")
        print(f"Target Frontend Directory: {frontend_dir}")

        if not frontend_dir.is_dir():
            print(
                f"Error: Frontend directory not found at expected path: {frontend_dir}",
                file=sys.stderr,
            )
            print(
                "Please ensure the 'script_runner/frontend' directory exists relative to your project root.",
                file=sys.stderr,
            )
            raise RuntimeError("Frontend directory not found.")

        try:
            print("Running npm install...")
            subprocess.check_call(["npm", "install"], cwd=frontend_dir)
            print("Running npm build...")
            subprocess.check_call(["npm", "run", "build"], cwd=frontend_dir)
        except subprocess.CalledProcessError as e:
            print(f"Error during npm build: {e}", file=sys.stderr)
            raise RuntimeError("Frontend build failed.") from e

        super().run()


if __name__ == "__main__":
    setup(
        cmdclass={"build": FrontendBuild},
    )
