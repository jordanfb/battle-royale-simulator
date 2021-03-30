"""
This is yet another attempt at a battle royale simulator. This one has tags! And other things! It's all very exciting.



I'm thinking a nice parser would be good, but I think I need to make my classes before I can figure out how to parse that data into them.

This is going to try to be multiple passes along the same narrative to build it up and make it more interesting and make it more readable and fun.

Who knows how well it will work.

"""

class Event:
	def __init__(self, time, fuck_if_I_know):
		self.time = time

class EventNarrative:
	def __init__(self):
		self.events = []

	def add_event(self, event):
		self.events += [event]

class Character:
	def __init__(self, name):
		self.name = name
		self.tags = []
		self.override_tags = []

	def add_tag(self, tag, length=-1):
		if tag not in self.tags:
			self.tags += [tag]

	def has_tag(self, tag):
		pass

	def __repl__(self):
		return self.name + ": " + ", ".join(self.tags)

	def __str__(self):
		return self.__repl__()

	def Parse(character_string):
		split = character_string.split(":")
		n = split[0].strip()
		c = Character(n)
		if len(split) > 1:
			tags = split[1].strip().split(",")
			for t in tags:
				c.add_tag(t.strip())
		return c

class Action:
	def __init__(self, name):
		self.name = name
		self.characters = []
		self.preconditions = []
		self.preconditions = []
		self.outcomes = []

	def functions_as_character(self, character, possible_agent):
		# does this character class match the other characters?
		pass

	def parse_fuckery_fuck(self):
		pass

class Tag:
	def __init__(self, string_to_parse):
		# pass in something like "subject.agent" "location.0", "subject.sees.object", "subject!scared", "object" and then figure it out.
		self.tag_string = string_to_parse
		self.split_values = string_to_parse.split(".")

	def is_tag_equal(self, other):
		if isinstance(other, Tag):
			return self == other
		return self == Tag(other) #otherwise it's a string that we need to parse to compare to!

	def __eq__(self, other):
		return self.tag_string == other.tag_string # this doesn't account for things like using "subject.sees.object" though so we'll have to figure this out

	def is_tag_satisfactory(self, tag):
		print("Oh dear this isn't implemented")
		return False

	def is_satisfied(self, list_of_tags):
		# this is passed a list of tags and has to check if it is satisfied by at least one of those tags
		for t in list_of_tags:
			if self.is_tag_satisfactory(t):
				return True
		return False


if __name__ == "__main__":
	c = Character.Parse("Jordan, agent_id.jordan: happy, joyful, location.0")
	print(c)
	# a = Action.Parse("attack: subject, object")
	print(isinstance(c, Tag))