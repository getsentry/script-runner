from typing import Any
from script_runner import read


@read
def do_stuff(config: dict[str, Any]):
    print("Doing stuff")


__all__ = ["do_stuff"]
