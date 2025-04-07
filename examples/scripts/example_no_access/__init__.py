from script_runner import read


@read
def do_stuff():
    print("Doing stuff")


__all__ = ["do_stuff"]
