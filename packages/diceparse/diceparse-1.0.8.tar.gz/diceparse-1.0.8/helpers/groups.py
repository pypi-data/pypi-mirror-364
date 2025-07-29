from lark import ParseTree


class DiceRoll:

    def __init__(self, tree: ParseTree):
        self.data = tree.data
        self.tree = tree

    @property
    def best(self) -> int:
        try:
            return int(self.tree.children[3].children[-1]) * (-1 if self.tree.children[3].children[0] == "-" else 1)
        except AttributeError:
            return 0

    @property
    def reroll(self) -> int:
        try:
            return int(self.tree.children[2].children[-1])
        except AttributeError:
            return 0

    @property
    def sides(self) -> int:
        try:
            return int(self.tree.children[1].children[-1])
        except AttributeError:
            return 1

    @property
    def quantity(self) -> int:
        return int(self.tree.children[0].children[-1])
