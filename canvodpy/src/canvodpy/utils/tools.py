from functools import wraps
import hashlib
import inspect
from pathlib import Path
import time
from typing import Any

from pydantic.dataclasses import dataclass
import tomli
from tqdm import tqdm

from canvodpy.logging.context import get_logger


def get_version_from_pyproject(pyproject_path=None):
    if pyproject_path is None:
        # Automatically find pyproject.toml at the project root
        # Adjust this if your structure changes
        pyproject_path = Path(__file__).resolve().parents[3] / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        data = tomli.load(f)
    return data["project"]["version"]


class TqdmUpTo(tqdm):

    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def isfloat(value):
    """To check if any variable can be converted to float or not"""
    try:
        float(value)
        return True
    except ValueError:
        return False


def cls_timer(msg: str, attr: str = None):
    """
    Decorator to time the execution of a class method.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            start = time.time()
            result = func(self, *args, **kwargs)
            end = time.time()

            # Retrieve the specified attribute if it exists
            attr_value = getattr(self, attr, "") if attr else ""
            attr_info = f" ({attr}: {attr_value})" if attr_value else ""

            formatting_dict = {
                "attr_name": attr,
                "attr_value": attr_value,
            }

            # Format the message by replacing placeholders with attribute values
            formatted_msg = msg.format(
                **formatting_dict) if "{" in msg else msg

            print(f"{formatted_msg} in {end - start:.2f} seconds")
            return result

        return wrapper

    return decorator


def enforce_keyword_only_methods(cls: Any) -> Any:
    """
    Decorator that modifies all methods in a class to enforce keyword-only arguments.
    """

    for name, method in cls.__dict__.items():
        if callable(method) and not name.startswith("__"):
            sig = inspect.signature(method)
            new_params = []

            for param in sig.parameters.values():
                if param.kind in {
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        inspect.Parameter.POSITIONAL_ONLY
                }:
                    param = param.replace(kind=inspect.Parameter.KEYWORD_ONLY)
                new_params.append(param)

            new_sig = sig.replace(parameters=new_params)

            @wraps(method)
            def wrapper(*args, **kwargs):
                bound_args = new_sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                return method(*args, **bound_args.arguments)

            setattr(cls, name, wrapper)

    return cls


def rinex_file_hash(path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA256 hash of a RINEX file's content."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    digest = h.hexdigest()[:16]
    log = get_logger()
    log.debug(f"Computed RINEX hash={digest} for {path}")
    return digest
