import json
import os
from math import ceil
from operator import add, sub, ge, gt, eq, ne, le, lt
from random import random, shuffle
from typing import Generator

from lark import Lark, ParseTree

from helpers.groups import DiceRoll


class DiceParser:
    """A dice roll parser!

    Attributes:
        default_type (str): The default name of untagged rolls.
        is_max (bool): Whether the first die of the last check was at max value.
        is_min (bool): Whether the first die of the last check was at min value.
        parser (Lark): The Lark parser instance loaded from the `lark` grammar file.
        results (list[dict[str, int | str]]): The current temporary results.
        skew_enabled (bool): Whether skewing dice rolls is enabled.
    """

    default_type: str
    is_max: bool
    is_min: bool
    parser: Lark
    results: list[dict[str, int | str]]
    skew_enabled: bool
    skew_operation: str
    current_string: str
    roll_string: str

    def __init__(self, skew_enabled: bool = True):
        """Create a DiceParser instance.

        Args:
            skew_enabled (bool, optional): Set whether skew is enabled on dice rolls. Defaults to True.
        """
        grammar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'grammar.lark')
        self.parser = Lark.open(grammar_path, propagate_positions=True)
        self.skew_enabled = skew_enabled
        self.default_type = "unknown"
        self.__reset()

    def __reset(self):
        """Initialize all of the variables that are used to store results, detect low/high dice rolls.
        """
        self.damage = dict()
        self.skew = 1
        self.skew_operation = "+"
        self.is_max, self.is_min = False, False
        self.results = list()

    def roll(self, text: str) -> list[dict[str, int | str]]:
        """Parse a roll string and generate the result.

        Args:
            text (str): The roll string to parse.

        Returns:
            list[dict[str, int | str]]: The results from the rolls in the roll string.
        """
        self.__reset()
        self.roll_string = text
        tree = self.parser.parse(text)
        self.process_roll(tree)
        return [i for i in self.results if i]

    def roll_as_json(self, text: str) -> str:
        """Parse a roll string and generate the results as JSON.

        Args:
            text (str): The roll string to parse.

        Returns:
            str: The JSON-representation of the results.
        """
        return json.dumps(self.roll(text), indent=2)

    def add_to_results(self) -> None:
        """Transfer the results from damage and into the results dictionary, then clear the damage.
        """
        if not self.damage:
            return
        self.damage["_roll"] = self.current_string
        self.results.append(dict(sorted(self.damage.items())))
        self.current_string = str()
        self.damage = dict()

    def add_damage(self, damage_type: str, damage: int) -> None:
        """Add damage amount and type to the damage variable.

        Args:
            damage_type (str): The damage type.
            damage (int): The damage amount.
        """
        try:
            self.damage[damage_type] += damage
        except KeyError:
            self.damage[damage_type] = damage

    def process_roll(self, tree: ParseTree):
        """Process the roll string ParseTree.

        Args:
            tree (ParseTree): The roll string post-parse.
        """
        for i in tree.children:
            if not i:
                continue
            match i.data:
                case "dice_types" | "roll_types":
                    self.update_substring(i)
                    self.process_roll(i)
                case "dice_group":
                    damage_type, damage = self.process_dice_group(i)
                    self.add_damage(damage_type, damage)
                case "skew":
                    self.skew = float(i.children[1])
                    if i.children[0]:
                        self.skew_operation = str(i.children[0].children[-1])
                    else:
                        self.skew_operation = "+"
                case "default_type":
                    self.default_type = str(i.children[0])
                case "dice_roll_t":
                    damage_type, damage = self.process_dice_roll_t(i)
                    self.add_damage(damage_type, damage)
                case "check":
                    self.update_substring(i)
                    self.process_check(i)
                case "count":
                    self.update_substring(i)
                    self.process_count(i)
                case "raw":
                    self.update_substring(i)
                    self.process_raw(i)

        if self.damage and i.data not in ["check", "count", "raw"]:
            self.damage["_total"] = sum(self.damage.values())
        self.add_to_results()

    def update_substring(self, i: ParseTree) -> None:
        """Update the current substring being processed.

        Args:
            i (ParseTree): The current ParseTree being processed.
        """
        self.current_string = self.roll_string[i.meta.start_pos:i.meta.end_pos]

    def process_raw(self, tree: ParseTree) -> None:
        d = DiceRoll(tree.children[0])
        values = sorted(self.roll_dice(d.quantity, d.sides, d.reroll, d.best, True), reverse=True)
        self.damage = {
            "_values": values,
            "_total": sum(values)
        }

    def process_count(self, tree: ParseTree) -> None:
        """Process the 'count' object and return the results.

        Args:
            tree (ParseTree): The ParseTree representation of a 'count'.
        """
        comp_dict = {
            ">": gt,
            "<": lt,
            ">=": ge,
            "<=": le,
            "=": eq,
            "==": eq,
            "!=": ne
        }

        comp = comp_dict[str(tree.children[1].children[-1])]
        d = DiceRoll(tree.children[0])
        comp_value = int(tree.children[2].children[-1])
        result = self.roll_dice(d.quantity, d.sides, d.reroll, d.best, True)

        self.damage = {
            "_total": sum(comp(i, comp_value) for i in result)
        }
        self.add_to_results()


    def generate_dice_rolls(self, quantity: int, sides: int, reroll: int = 0) -> Generator[int, any, any]:
        """Generate die rolls given the number of sides and the quantity of dice to roll.

        Args:
            quantity (int): The number of dice to roll.
            sides (int): The number of sides each die has.

        Yields:
            int: The result of a die roll.
        """
        for _ in range(quantity):
            roll = max(ceil(self.__random() * sides), 1)
            if roll <= reroll:
                roll = max(ceil(self.__random() * sides), 1)
            yield roll

    def process_check(self, tree: ParseTree) -> None:
        """Process a check and return the results.

        Args:
            tree (ParseTree): The "check" ParseTree.
        """
        adv_type = None
        results = list()
        rolls = 1

        if a := tree.children[0]:
            adv_type = str(a)

        if adv_type:
            rolls = 2

        for _ in range(rolls):
            temp_damage = 0
            roll_state = "normal"
            current_op = add
            for idx, t in enumerate(tree.children[1:]):
                match t.data:
                    case "dice_roll":
                        temp_damage = current_op(
                            temp_damage, self.process_dice_roll(t))
                        if idx == 0:
                            sides = int(t.children[1].children[-1])
                            if self.is_max:
                                roll_state = f"natural {sides}"
                            if self.is_min:
                                roll_state = "natural 1"
                    case "operation":
                        if o := t.children[-1]:
                            current_op = {"+": add, "-": sub}[o]
            results.append((temp_damage, roll_state))

        match adv_type:
            case "dis":
                results = sorted(results, key=lambda x: x[0])[0]
            case "adv":
                results = sorted(results, key=lambda x: x[0], reverse=True)[0]
            case _:
                results = results[0]

        self.damage = {
            "status": results[1],
            "_total": results[0]
        }
        self.add_to_results()

    def process_dice_group(self, tree: ParseTree) -> tuple[str, int]:
        """Process a dice group tree.

        Args:
            tree (ParseTree): The dice group tree to process.

        Returns:
            tuple[str, int]: The damage and damage type of the result.
        """
        multiplier = 1
        multiplier_pre, multiplier_post = 1, 1
        multiplier_op = None
        damage_type = self.default_type
        damage = 0

        if m := tree.children[0]:
            multiplier = int(m.children[0])
            multiplier_op = str(tree.children[1])
        
        match multiplier_op:
            case "x":
                multiplier_post = multiplier
            case "*":
                multiplier_pre = multiplier

        if t := tree.children[-1]:
            damage_type = str(t.children[0])

        for _ in range(multiplier_pre):
            current_operator = add
            temp_damage = 0
            for i in tree.children[2:-1]:
                match i.data:
                    case "dice_roll":
                        temp_damage = current_operator(
                            temp_damage, self.process_dice_roll(i))
                    case "operation":
                        if o := i.children[-1]:
                            current_operator = {'+': add, '-': sub}[o]
            damage += max(temp_damage, 1)
        return (damage_type, damage * multiplier_post)

    def process_dice_roll_t(self, tree: ParseTree) -> tuple[str, int]:
        """Process a 'dice roll with type' (`dice_roll_with_t`) tree.

        Args:
            tree (ParseTree): The `dice_roll_with_t` tree to process.

        Returns:
            tuple[str, int]: The damage type and damage amount.
        """
        dice_roll, t = tree.children
        damage_type = str(t.children[0]) if t else self.default_type

        result = self.process_dice_roll(dice_roll)

        return (damage_type, result)

    def process_dice_roll(self, tree: ParseTree) -> int:
        """Process a `dice_roll` and return the amount.

        Args:
            tree (ParseTree): The `dice_roll` to process.

        Returns:
            int: The amount rolled.
        """
        d = DiceRoll(tree)
        return self.roll_dice(d.quantity, d.sides, d.reroll, d.best)
    
    def __random(self) -> float:
        """Generate a random number between 0 and 1.

        Returns:
            float: The random number.
        """
        r = random()
        if self.skew == 0:
            return r
        
        match self.skew_operation:
            case "+":
                return r ** (1 / self.skew)
            case "-":
                return 1 - ((1 - r) ** (1 / self.skew))
            case _:
                return r

    def roll_dice(self, quantity: int, sides: int, reroll: int, best: int, raw: bool = False) -> int | list[int]:
        """Roll a set of dice.

        Args:
            quantity (int): The number of dice to roll.
            sides (int): The number of sides per die.

        Returns:
            int: The total rolled across all the dice.
        """
        if sides <= 1 or not quantity:
            return quantity

        self.is_max = False
        self.is_min = False

        if best:
            if best < 0:
                best = abs(best)
                reverse = False
            elif best > 0:
                reverse = True
            rolls = list(self.generate_dice_rolls(quantity, sides, reroll))
            rolls = sorted(rolls, reverse=reverse)[:best]
            shuffle(rolls)
            first_roll = rolls.pop()
        else:
            rolls = self.generate_dice_rolls(quantity, sides, reroll)
            first_roll = next(rolls)

        if raw:
            return [first_roll] + list(rolls)

        if first_roll == 1:
            self.is_min = True
        elif first_roll == sides:
            self.is_max = True

        return first_roll + sum(r for r in rolls)
