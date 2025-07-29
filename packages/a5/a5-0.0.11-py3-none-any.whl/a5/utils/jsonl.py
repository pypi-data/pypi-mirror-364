import json
from pathlib import Path
from tqdm import tqdm
from contextlib import contextmanager
import threading

def jsonl_reader(path: Path):
    with path.open(encoding="utf-8") as fi:
        for line in tqdm(fi):
            yield json.loads(line)

def dump_line(data):
    return json.dumps(data, ensure_ascii=False)

@contextmanager
def jsonl_writer(path: Path):
    write_lock = threading.Lock()

    with path.open("a", encoding="utf-8") as fo:
        def _writer(data):
            with write_lock:
                fo.write(dump_line(data) + "\n")

        yield _writer

# with jsonl_writer(Path("test.jsonl")) as write:
#     write({"hi": "Hello"})

# for obj in jsonl_reader(Path("test.jsonl")):
#     print(obj)
