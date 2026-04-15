# Python idiom examples

On-demand reference — not auto-loaded. Read this when you need a concrete before/after
pattern for the idioms described in the `## Python projects` section of the engineering
standards.

---

## 1. Guard clauses (flat over nested)

```python
# Before — deeply nested
def process(data):
    if data is not None:
        if len(data) > 0:
            result = []
            for item in data:
                if item.is_valid():
                    result.append(item.value)
            return result
        return []
    return []

# After — guard clauses + comprehension
def process(data):
    if not data:
        return []
    return [item.value for item in data if item.is_valid()]
```

---

## 2. `@dataclass` over manual `__init__`

```python
# Before
class Point:
    def __init__(self, x: float, y: float, label: str = "") -> None:
        self.x = x
        self.y = y
        self.label = label

    def __repr__(self) -> str:
        return f"Point(x={self.x}, y={self.y}, label={self.label!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x, self.y, self.label) == (other.x, other.y, other.label)

# After
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    label: str = ""
```

---

## 3. `Enum` over string constants

```python
# Before
STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_DONE    = "done"

def handle(status: str) -> None:
    if status == STATUS_PENDING:
        queue()
    elif status == STATUS_RUNNING:
        wait()
    elif status == STATUS_DONE:
        finalize()

# After
from enum import Enum

class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE    = "done"

def handle(status: Status) -> None:
    match status:
        case Status.PENDING:  queue()
        case Status.RUNNING:  wait()
        case Status.DONE:     finalize()
```

---

## 4. `pathlib` over `os.path`

```python
# Before
import os

config_dir  = os.path.join(os.path.dirname(__file__), "config")
config_path = os.path.join(config_dir, "settings.json")

if os.path.exists(config_path):
    with open(config_path) as f:
        data = f.read()

output = os.path.join(config_dir, "output.json")
with open(output, "w") as f:
    f.write(data)

# After
from pathlib import Path

config_dir  = Path(__file__).parent / "config"
config_path = config_dir / "settings.json"

if config_path.exists():
    data = config_path.read_text()

(config_dir / "output.json").write_text(data)
```

---

## 5. `collections` shortcuts

```python
# Before — manual counting
word_counts: dict[str, int] = {}
for word in words:
    if word not in word_counts:
        word_counts[word] = 0
    word_counts[word] += 1

# After — Counter
from collections import Counter
word_counts = Counter(words)

# Before — manual grouping
groups: dict[str, list[str]] = {}
for item in items:
    key = item.category
    if key not in groups:
        groups[key] = []
    groups[key].append(item.name)

# After — defaultdict
from collections import defaultdict
groups: dict[str, list[str]] = defaultdict(list)
for item in items:
    groups[item.category].append(item.name)
```
