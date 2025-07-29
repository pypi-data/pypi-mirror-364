**DiceParser** is a robust dice-rolling program that can accomplish quite a lot of different kinds of rolls to include attack/damage rolls, skill checks, and even weighting dice rolls to include _advantage_ and _disadvantage_ rolls.

**DiceParser** can also categorize multiple different types of results such as damage types in the same roll with a simple syntax.

## Installation

Simply add the `diceparse` package to your project.  For example, for `uv`:

```
uv add diceparse
```

### Quick Example

```python title="Python Code" linenums="1"
from diceparser import DiceParser

dice = DiceParser()
result = dice.roll("3d8+10")
print(result)
```

```json title="Result"
[
  {
    "_roll": "1d8+3",
    "_total": 4,
    "unknown": 4
  }
]
```

!!! note
    Unfortunately, I couldn't call the PyPI package `diceparser` which is annoying.  However, the package is called `diceparse` and you import `diceparser`.

