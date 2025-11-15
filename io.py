import os
import json
from glob import glob
from typing import Iterator, Any, List


def iter_jsonl(path: str) -> Iterator[Any]:
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                yield line


def iter_json(path: str) -> Iterator[Any]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        for it in data:
            yield it
    else:
        yield data


def iter_sources(source: str) -> Iterator[str]:
    if os.path.isdir(source):
        files: List[str] = []
        files.extend(glob(os.path.join(source, '*.jsonl')))
        files.extend(glob(os.path.join(source, '*.json')))
        for fp in files:
            yield fp
    else:
        yield source