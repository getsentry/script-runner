"""
experimental
"""

import subprocess
from typing import Any

from script_runner import get_function_context, write


@write
def get_pods() -> Any:
    """
    view the script runner pods
    """

    region = get_function_context().region
    namespace = "script-runner"

    cmd = [
        "sentry-kube",
        "-C",
        region,
        "kubectl",
        "get",
        "pods",
        "--namespace",
        namespace,
        "--output",
        "json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {result.stderr}")

    return result.stdout


__all__ = [
    "get_pods",
]
