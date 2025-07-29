# Rolling Dice

A dice rolling library written in Python that uses `lark` to parse dice rolls with a surprising number of features!

- Online documentation: [https://dice.jamesthebard.net](https://dice.jamesthebard.net)
- Source repository: [https://codeberg.org/JamesTheBard/dice-roller](https://codeberg.org/JamesTheBard/dice-roller)

## Installation

### From PyPI

Simply add the `diceparse` package as a dependency in your project.

### From Git

#### Requirements

- Python version 3.11 or greater
- The [`uv` dependency manager](https://docs.astral.sh/uv/) to handle dependency installation and virtual environment creation

To get everything setup:

```console
$ uv venv
$ uv sync
```

## Usage

A quick example to get rolling:

```python
from diceparser import DiceParser

dice = DiceParser()
result = dice.roll("1d8+3")
print(result)
```

```json
[
  {
    "_roll": "1d8+3",
    "_total": 4,
    "unknown": 4
  }
]
```

## Documentation

You can view the documentation by either going to the [online documentation](https://dice.jamesthebard.net) or by cloning the repo and running it locally on your computer with the following commands.  It will be accessible at [`http://127.0.0.1:8000`](http://127.0.0.1:8000).

```shell
$ uv sync --group docs
$ source .venv/bin/activate
$ mkdocs serve
```

```
INFO    -  Building documentation...
INFO    -  Cleaning site directory
INFO    -  Documentation built in 0.14 seconds
INFO    -  [11:41:03] Watching paths for changes: 'docs', 'mkdocs.yml'
INFO    -  [11:41:03] Serving on http://127.0.0.1:8000/
```