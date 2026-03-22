import importlib


def import_attr(path: str, attr_name: str | None = None):
    if not attr_name:
        paths = path.split(".")
        module_path = ".".join(paths[:-1])
        attr_name = paths[-1]
    else:
        module_path = path

    module = importlib.import_module(module_path)
    return getattr(module, attr_name, None)
