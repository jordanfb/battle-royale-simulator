"""
This is a test to see how well this tagged objects class works for running events etc. for an agent based simulation.



events would be something like:

event attack_with_sword:
	[a] attacks [b] with fuckery
"""


class TaggedObject:
	def __init__(self, name):
		self.name = name
		self.tags = {} # {location:["this tag is set to bob", { "subtag": [5,{}] }], } # basically a recursive list of all the tags and their values and the subtag values

	def remove_tag(self, tag):
		recursive_level = self.tags
		split_tag = tag.split(".")
		for sub_tag in split_tag[:-1]:
			if sub_tag not in recursive_level:
				print("Tag doesn't exist")
				return None# can't remove it it doesn't exist!
			else:
				recursive_level = recursive_level[sub_tag][1]
		return recursive_level.pop(split_tag[-1], None)
		
	def set_tag(self, tag, value):
		split_tag = tag.split(".") # get all the subtags
		recursive_level = ["", self.tags]
		for sub_tag in split_tag:
			if sub_tag not in recursive_level[1]:
				recursive_level[1][sub_tag] = [None, {}]
			recursive_level = recursive_level[1][sub_tag]
		recursive_level[0] = value # store the value for that tag!

	def get_tag(self, tag):
		split_tag = tag.split(".") # get all the subtags
		recursive_level = self.tags
		for sub_tag in split_tag[:-1]:
			if sub_tag not in recursive_level:
				return None
			recursive_level = recursive_level[sub_tag][1]
		return recursive_level[split_tag[-1]]

	def has_tag(self, tag):
		split_tag = tag.split(".") # get all the subtags
		recursive_level = self.tags
		for sub_tag in split_tag:
			if sub_tag not in recursive_level:
				return False
			recursive_level = recursive_level[sub_tag][1]
		return True

	def __repl__(self):
		return str(self)

	def __str__(self):
		s = self.name + ": " + str(self.tags)
		return s
