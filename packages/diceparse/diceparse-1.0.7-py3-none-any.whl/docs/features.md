## Skewing

!!! note
    This must be specified before any rolls are definied as in the example below.  Also, this is a _global_ option and will effect all of the dice rolls.

    ```python title="Example Roll"
    dice.roll("^1.2 check(1d20+3)")
    ```

    In version `1.0.4` and later, you can change the default skew at the beginning of every chained dice roll.

    ```python title="Example Roll"
    dice.roll("^1.2 check(1d20+3),^2 (2d10+3)[fire]")
    ```

Skewing allows for the weighting of dice towards either the maximum or the minimum for each die rolled.  It's available for both regular rolls and checks.

### Positive Skew

A positive skew value (e.g. `^2` or `^+2`) greater than one shifts the rolls towards the maximum value while positive skew value less than one shifts it towards one.  This can be useful in more than a few ways such as granting the effects of _advantage_ to all dice rolled.

The following two examples result in the same rolls statistically:

```python title="Example Rolls"
dice.roll("^2 check(1d20)")
dice.roll("check adv(1d20)")
```

The following formula used to shift the results.

```
random_value_skewed = random_value_normal ^ (1 / skew_value)
```

### Negative Skew

A negative skew value (e.g. `^-2`) greater than 1 shifts the rolls towards one while a negative skew value less than one shifts it towards the maximum.  A negative skew value shifts a number towards the maximum in the way a positive skew value shifts it to 1.

You can use negative skew values to apply _disadvantage_ in the same way positive skew values apply _advantage_.  The following two values are the same things statistically:

```python title="Example Rolls"
dice.roll("^-2 check(1d20)")
dice.roll("check dis(1d20)")
```

The following formula used to shift the results.

```
random_value_skewed = 1 - ((1 - random_value_normal) ^ (1 / skew_value))
```

!!! note "Mathematics and Random Numbers"
    The `random_value_normal` value is a random number that is generated on the open interval of (0, 1).  Once the math is done mathing, the `random_value_skewed` is also on the interval of (0, 1).  The `random_value_skewed` is then multiplied by the number of sides of the die and then rounded up via the `ceil` function to get the result.

    Also, the reason that the formulas were chosen is that a given skew value represents the advantage (if positive) or disadvantage (if negative) of the roll.  A skew of `2` is roll-two-keep-the-best (a.k.a. _advantage_).  A skew of `3` is roll-three-keep-the best (a.k.a. _double advantage_ or the thing the GM won't let you have because _advantage_ doesn't stack).

    In short: positive values of skew work out to "roll that many dice and keep the best one" and negative values of skew work out to "roll that many dice and keep the worst one".

## Tagging

!!! warning
    You can use custom tags in two places: after a dice group or after part of a roll.  You cannot use custom tags inside of a dice group nor can you use them in a check.  The examples below are all valid.

    ```python
    dice.roll("(3d8+10)[lightning]")
    dice.roll("2d8[fire]+3")
    dice.roll("1d4+9[holy]")
    ```

Tagging is the ability to assign a category to the result of part of the roll.  In the example below, we've assigned the `fire` tag to the first part of the results.  Note that the results of the `2d4` part are categorized as `unknown` because it isn't tagged.  Any part of a roll that is untagged falls under the `unknown` category.

```python title="Example Roll"
dice.roll("3d8[fire]+2d4")
```

```json title="Result"
[
  {
    "_roll": "3d8[fire]+2d4",
    "_total": 25,
    "fire": 18,
    "unknown": 7
  }
]
```

### Default Tag

You can override the default category in a roll by enclosing the tag in greater-than and less-than signs (e.g. `<` and `>`).  To rename the default category to `generic`, you could do the following in the roll:

```python title="Example Roll"
dice.roll("<generic>3d8[fire]+2d4")
```

```json title="Result"
[
  {
    "_roll": "3d8[fire]+2d4",
    "_total": 25,
    "fire": 18,
    "generic": 7
  }
]
```

In version `1.0.4` or later, you can set the default damage type at the beginning of every chained roll.

```python title="Example Roll"
dice.roll("<generic>3d8[fire]+2d4,<cool_damage>(2d20+10)")
```

```json title="Result"
[
  {
    "_roll": "3d8[fire]+2d4",
    "_total": 15,
    "fire": 12,
    "generic": 3
  },
  {
    "_roll": "(2d20+10)",
    "_total": 23,
    "cool_damage": 23
  }
]
```

Default tags must be declared at the start of the roll before any rolls are defined.  Also, it is global and will apply for the entirety of the roll unless defined later at the start of another chained roll.

!!! info "Allowed Charaters"
    - **Version 1.0.0**: Tags can only have lowercase letters.

    - **Version 1.0.4**: Tags can have lowercase and uppercase letters along with an underscore.  They cannot begin with an underscore.

## Advantage/Disadvantage

!!! note
    This is only applicable to checks.  If you want to apply _advantage_ or _disadvantage_ to standard rolls, you can skew them using `^2` and `^-2` respectively.

Advantaged and disadvantaged checks are a staple in D&D, and both can be applied to checks.

Examples of checks with advantage:

```python title="Example Rolls"
dice.roll("check adv(1d20+12)")
dice.roll("cadv(1d20+12)")
```

Examples of checks with disadvantage:

```python title="Example Rolls"
dice.roll("check dis(1d20+12)")
dice.roll("cdis(1d20+12)")
```

## Multiplication

!!! note
    This is only available at the start of dice groups and not for things like checks.

Multiplication allows for multiplying the result of a dice group by a given value.  There are two types of multiplication: _pre-roll_ and _post-roll_.

### Pre-Roll Multiplication

Pre-roll multiplication takes the dice group and multiplies the rolls before actually rolling them.  The following example shows two rolls that are exactly the same.  Pre-roll multiplication uses the `*` operator.

```python title="Example Rolls"
dice.roll("4*(1d8)")
dice.roll("(1d8+1d8+1d8+1d8)")
```

```json title="Result"
[
  {
    "_roll": "4*(1d8)",
    "_total": 22,
    "unknown": 22
  }
]
```

### Post-Roll Multiplication

Post-roll multiplication takes the result of the dice group and then multiplies it.  This is the standard way for damage in games like _Pathfinder_ on a critical and is signified with the `x` operator.

```python title="Example Roll"
dice.roll("2x(2d10+1)")
```

```json title="Result"
[
  {
    "_roll": "2x(2d10+1)",
    "_total": 12,
    "unknown": 12
  }
]
```

## Subtraction

!!! warning
    Currently, subtraction is only available for checks and dice groups.  Checks can go negative, and standard rolls cannot go below 1 at the moment which is why they cannot be used outside of dice groups for those regular rolls.

Subtraction allows you to add penalties to rolls and are pretty easy: just use a `-` sign.  In the following example, a `-1` penalty is being applied to a dice roll inside of a dice group.

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

## Rerolling Dice

!!! note
    Supported in version `1.0.5`.

You can specify during standard rolls and checks the number of dice to reroll if the result is less-than-or-equal-to a given value using the `reroll` or `!` operator.  This will reroll any die that is less-than or equal to the value once.

For example, if you specify `4d6 reroll 2` or `4d6!2` it will reroll any initial roll that results in a 2 or less.  You can still get a 2 or less in the second roll though.

```python title="Example Rolls"
dice.roll("(4d6!1)[fire]")
dice.roll("(4d6 reroll 1)[fire]")
```

```json title="Result"
[
  {
    "_roll": "(4d6!1)[fire]",
    "_total": 17,
    "fire": 17
  }
]
```

!!! warning
    If you are rerolling dice and keeping dice, the `reroll` operator has to come before the `keep` operator.  For example, you can specify:

    ```python
    dice.roll("4d6!2k3")
    dice.roll("4d6 reroll 2 keep 3")
    ```

    You cannot specify them the other way around:

    ```python
    dice.roll("4d6k3!2")
    dice.roll("4d6 keep 3 reroll 2")
    ```

## Keeping Dice

!!! note
    Supported in version `1.0.5`.

You can specify the number of dice to keep in a check or regular roll via the `keep` or `k` operator.  This will keep the number of dice specified with the highest value(s) if the number after `keep` is positive, and the lowest value(s) if the number is negative.

```python title="Example Rolls"
dice.roll("(4d6k3)[fire]")
dice.roll("(4d6 keep 3)[fire]")
```

```json title="Result"
[
  {
    "_roll": "(4d6k3)[fire]",
    "_total": 16,
    "fire": 16
  }
]
```

!!! info "Advantage and Disadvantage"
    You can also use `keep` for _advantaged_ and _disadvantaged_ rolls as well.  Advantage is just rolling two dice and keeping the highest one.

    ```python title="Advantage Roll Example"
    dice.roll("2d20 keep 1")
    ```

    Disadvantage is just rolling two dice and keping the lowest one.

    ```python title="Disadvantage Roll Example"
    dice.roll("2d20 keep -1")
    ```

!!! warning
    If you are rerolling dice and keeping dice, the `reroll` operator has to come before the `keep` operator.  For example, you can specify:

    ```python
    dice.roll("4d6!2k3")
    dice.roll("4d6 reroll 2 keep 3")
    ```

    You cannot specify them the other way around:

    ```python
    dice.roll("4d6k3!2")
    dice.roll("4d6 keep 3 reroll 2")
    ```