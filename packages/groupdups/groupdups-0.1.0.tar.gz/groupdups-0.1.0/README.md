# groupdups

A simple Python package to group duplicate values in a list and return their index positions.

## Installation

```bash
pip install groupdups
```

## Usage

```python
from groupdups import group_duplicates

arr = [2, 3, 2, 4, 3, 2]
print(group_duplicates(arr))
# Output: {2: [0, 2, 5], 3: [1, 4], 4: [3]}
```
