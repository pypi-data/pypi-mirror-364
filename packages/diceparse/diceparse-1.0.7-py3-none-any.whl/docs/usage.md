All rolls are passed as string to the `roll()` method which return a Python list of the results and the `roll_as_json()` method which returns the results as JSON making it very useful to use with programs like `jq`.

There are four kinds of rolls: _standard_, _checks_, _counts_, and _raw_.

## Standard Rolls

Standard rolls are really just that: pretty bog standard sets of rolls.  They can be grouped together in dice groups, tagged for things like damage types like _fire_ and _lightning_, and even multiplied for repetitive rolls.

```python title="Example Roll"
dice.roll("(2d6+10)[fire]+1d6[holy]+2d8+6")
```

```json title="Result"
[
  {
    "_roll": "(2d6+10)[fire]+1d6[holy]+2d8+6",
    "_total": 31,
    "fire": 17,
    "holy": 1,
    "unknown": 13
  }
]
```

### Features Available
- Skewing
- Dice groups
- Subtraction (in dice groups)
- Tagging
- Reroll Dice (version `1.0.5`)
- Keep Dice (version `1.0.5`)

## Checks

Checks are rolls where the parser keeps track of the first die/dice rolled to see if it was a natural 1 or a natural maximum.  These are especially useful for games like _Pathfinder_ and _Dungeons and Dragons_ (or just `d20` systems in general) when determining whether saves and skill checks are successful.

Checks can also be rolled at _advantage_ or _disadvantage_ depending on the situation as well.

```python title="Example Roll"
dice.roll("check adv(1d20+10)")
```

```json title="Result"
[
  {
    "_roll": "check adv(1d20+10)",
    "_total": 30,
    "status": "natural 20"
  }
]
```

!!! tip Shorthand
    Checks can either be spelled out like `check (1d20)` or condensed into `c(1d20)` which makes things a bit easier.  Also the parser ignores whitespace as long as it doesn't make things ambiguous.

!!! warning
    Checks only check the first die rolled to see if it was a `natural 1` or the max die value.

    ```python
    dice.roll("check(2d10)")
    ```

    In the example above, the first d10 is checked to see if it's the minimum or maximum value.  The result of that specific die roll is what is placed into the `status` field in the return value.


### Features Available
- Skewing
- Subtraction
- Advantage/Disadvantage
- Reroll Dice (version `1.0.5`)
- Keep Dice (version `1.0.5`)

## Dice Counts

!!! note
    Supported in version `1.0.2`.

!!! info "Short Hand"
    The short hand for counts is the `#` sign, supported in version `1.0.4` or greater.  Also, the `==` operator is supported in version `1.0.4` or greater.

You can roll _counts_ where you roll a number of dice and compare them against a value.  The table below shows the operators you can use:

| Operator | Example | Meaning |
|:-:|:-:|:--|
| `=`, `==`  | `count(4d10)=4`  | Count all of the rolls that are equal to 4. |
| `!=` | `count(4d10)!=4` | Count all of the rolls that are not equal to 4. |
| `>`  | `count(4d10)>4`  | Count all of the rolls that are greater than 4. |
| `>=` | `count(4d10)>=4` | Count all of the rolls that are greater than or equal to 4. |
| `<`  | `count(4d10)<4`  | Count all of the rolls that are less than 4. |
| `<=` | `count(4d10)<=4` | Count all of the rolls that are less than or equal to 4. |

!!! warning 
    _Count_ rolls can only have one set of dice rolled (e.g. `4d10`) and not multiple sets of dice (e.g. `4d10+3d8` or `4d10+3`).

```python title="Roll Example"
dice.roll("#(8d10)>5")
dice.roll("count(8d10)>5")
```

```json title="Result"
[
  {
    "_roll": "count(8d10)>5",
    "_total": 3
  }
]
```

### Features Available
- Skew
- Reroll Dice (version `1.0.5`)
- Keep Dice (version `1.0.5`)

## Raw Rolls

!!! note
    Supported in version `1.0.5`.

Raw rolls simply roll the dice and return the results.  It can only roll one set of dice, but it does allow you to keep dice and reroll dice.  Raw rolls start with the `raw` or `r` instruction.

```python title="Roll Examples"
dice.roll("raw(4d6 reroll 1 keep 3)")
dice.roll("r(4d6!1k3)")
```

```json title="Result"
[
  {
    "_roll": "raw(4d6 reroll 1 keep 3)",
    "_total": 11,
    "_values": [4, 4, 3]
  }
]
```

### Features Available

- Skew
- Reroll Dice
- Keep Dice

## Roll Chaining

You can combine regular rolls and checks together using commas which will can make things a bit easier.  The example below shows how a check and a standard roll is in the same line and the result of the roll.

```python title="Example Roll"
dice.roll("check(1d20+3),(1d8+3)[slashing]")
```

```json title="Result"
[
  {
    "_roll": "check(1d20+3)",
    "_total": 9,
    "status": "normal"
  },
  {
    "_roll": "(1d8+3)[slashing]",
    "_total": 4,
    "slashing": 4
  }
]
```

## Dice Groups

Dice groups are a basic way to roll complex combinations of dice and modifiers while also tagging them.  Basically a way to group dice.  Dice groups also have a minimum result of 1 for things like dagger damage (`1d4-1`).

```python title="Example Roll"
dice.roll("(1d4-1)[piercing]")
```

```json title="Result"
[
  {
    "_roll": "(1d4-1)[piercing]",
    "_total": 1,
    "piercing": 1
  }
]
```