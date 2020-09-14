import importlib.util
import os

import yaml
from flask import Flask


def load_config(app: Flask):
    path = package_path("configuration")
    with open(os.path.join(path, "app.yaml")) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        app.config.from_mapping({"APP": config})


def package_path(package_name: str) -> str:
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        raise ImportError('Not a package: %r', package_name)

    for path in spec.submodule_search_locations:
        return path
