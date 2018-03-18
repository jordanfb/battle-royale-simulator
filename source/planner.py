"""
This file has all of the classes for the AI GOAP planner. I decided to use a GOAP planner instead of a HTN or utility or state machine because it fits what I would
love this to become -- all of the tributes planning how to kill eachother using the various mechanics of the arena.

classes in this file:
GOAP planner
worldstate -- used to represent goal states and used by the planner when backstepping through reality.
actionrepresentation

"""


class ActionRep:
	def __init__(self):
		pass

	def get_prereqs(self):
		pass

	def get_effects(self):
		pass

	def apply_effects(self, worldstate):
		pass

	def are_effects_useful(self, worldstate):
		"""returns whether or not the effects of this action influence the needed changes in the worldstate in some way"""
		return False

class Worldstate:
	"""used by the planner to represent goals and states of the world after doing actions.
	When part of this worldstate isn't represented already it can get what the current value is from the world it is representing
	or perhaps it instead there's just a special worldstate (i.e. the world) that can be compared to worldstates?
	We create the worldstate representing each of the goals of the AI brains at their initialization, which probably means that this should be able to be read this in from
	a text file...
	Goal:
	What goals do the tributes have?
	kill tribute 1
	kill tribute 2
	kill tribute 3
	kill tribute 4
	or just kill other tributes?
	for all items tagged "tribute" if item != self then health <= 0 # why bother with checking if it's exactly 0, that's silly, overkill is better.
	Flee goal -- if getScaredValue() > 33% then try to get away?
	"""
	def __init__(self, world):
		self.realworld = realworld

	def compare_to(self, other_worldstate):
		pass

	def is_satisfied(self, world):
		# returns true or false if all of the requirements are satisfied by the world that is passed in.
		pass

	def copy(self):
		# returns a copy of itself
		pass



