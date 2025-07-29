import sys

from diceparser import DiceParser

# Create a DiceParser object
d = DiceParser()

# Grab the dice roll from the system "argv".  This is the equivalent of:
# =======================================================================
# import json
# results = d.roll(sys.argv[1])
# results = json.dumps(results)
# -----------------------------------------------------------------------
# results = d.roll_as_json(sys.argv[1])

# Print the results
# print(d.roll(sys.argv[1]))
print(d.roll_as_json(sys.argv[1]))
# print(d.parser.parse(sys.argv[1]).pretty())