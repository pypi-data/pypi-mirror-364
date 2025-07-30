import json
import yaml
from deepdiff import DeepDiff
from typing import Optional

def load_file(path: str):
    if path.endswith('.json'):
        with open(path) as f:
            return json.load(f)
    elif path.endswith(('.yaml', '.yml')):
        with open(path) as f:
            return yaml.safe_load(f)
    else:
        raise ValueError("Unsupported file format")

def compute_diff(
    file1: str,
    file2: str,
    exclude_paths: Optional[list[str]] = None,
    exclude_regex_paths: Optional[list[str]] = None,
    include_paths: Optional[list[str]] = None,
    ignore_order: bool = False,
    significant_digits: Optional[int] = None,
    raw: bool = False
) -> str:
    data1 = load_file(file1)
    data2 = load_file(file2)
    diff = DeepDiff(
        data1,
        data2,
        view='tree',
        exclude_paths=exclude_paths or [],
        exclude_regex_paths=exclude_regex_paths or [],
        include_paths=include_paths or [],
        ignore_order=ignore_order,
        significant_digits=significant_digits
    )
    return diff.to_json() if raw else diff.pretty()
