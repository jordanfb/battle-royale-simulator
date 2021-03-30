# interpreter.py
# This is meant to interpret a list of actions between tagged characters to flush out the language more
# for instance if we have a "scared" jordan then bob attack jordan becomes "bob swung at jordan, the blade missing by an inch"
# This is going to try to be a stand alone file, so we're going to recreate the model of the world from the text we're fed in I think? It may make more sense
# just to be handed a model but I like it this way I think it'll be interesting to try out.

"""
Maybe instead of tags they're basically tables?

Jordan.Scared = true
Jordan.Location = 1
Jordan.Relationship.Bob = good


SetTag Jordan.Location.Test True # adds the jordan.bobfuckery tag and the subtag test and sets that to true
RemoveTag Jordan.Location # removes all the tags under bobfuckery in the hierarchy

So a tag can be anything but also can have subtags, so if it has no subtag

So events we currently handle are 

set_tag
remove_tag
get_tag
has_tag

now we need a way to interpret sentences
event: Jordan attacks Joe # we intercept the action using a dictionary key, then we need a way to determine what to choose depending on what keys we have

person_a pulls out a sword
person_a swings [adv_attack] at person_b [narrowly missing{person_b.emotions.scared}||]

attack : ["a", "b", [
					[required keys, optional keys, "a swings a [random a.inventory.weapons] at b"],
					[],
					]]

[a] attack [b]:
	[b].perspective [b].emotions.scared
		[a.name] swings wildly at [b.name] and scores a hit.
		[a.name] swings at [b.name], almost killing [b.pronouns.object.3rd].
	[a].perspective [a].emotions.excited
		[a.name] lunges at [b.name]
	default
		[a.name] swings at [b.name]
		[a.name] attacks [b.name]
[a] misses [b]:
	[b].perspective [b].emotions.scared
		[a.name] swings wildly at [b.name], narrowly missing.
		[a.name] swings at [b.name], but [b.name] dodges the attack.
	[a].perspective [a].emotions.excited
		[a.name] lunges at [b.name] but misses.
	default
		[a.name] swings at [b.name]
		[a.name] attacks [b.name]



create_item 12345 Jordan
set_tag 12345.name Jordan
set_tag 12345.location 1
set_tag 12345.pronouns.subject.1 I
set_tag 12345.pronouns.subject.2 you
set_tag 12345.pronouns.subject.3 he
set_tag 12345.pronouns.object.1 me
set_tag 12345.pronouns.object.2 you
set_tag 12345.pronouns.object.3 him
set_tag 12345.pronouns.possesive.1 my
set_tag 12345.pronouns.possesive.2 your
set_tag 12345.pronouns.possesive.3 his
set_tag 12345.emotions.scared True
set_tag 12345.skills.sword True

... same for a bunch of other characters

event 12345 runs away.
set_tag 12345.location 2
event 6789 pick_up_weapon
set_tag 6789.inventory.weapons.spear True


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


def test_tagged_object():
	a = TaggedObject("a")
	a.set_tag("location.1.surroundings", "hello")
	print("a has tag surroundings " + str(a.has_tag("location.1.surroundings")))
	print("a has tag 1 " + str(a.has_tag("location.1")))
	print("a has tag 2 " + str(a.has_tag("location.2")))
	print(a)
	print()
	a.set_tag("location.1.bob", "dead")
	a.set_tag("location.2.surroundings", "hello")
	a.remove_tag("location.1.surroundings")
	print("a has tag 1.surroundings " + str(a.has_tag("location.1.surroundings")))
	print("a has tag 2 " + str(a.has_tag("location.2")))
	print("a tag 2 value " + str(a.get_tag("location.2")))
	print(a)
	print()

	a.remove_tag("location.2")
	print("a has tag 2 " + str(a.has_tag("location.2")))
	print("a has tag 1 " + str(a.has_tag("location.1")))
	print(a)
	print()

	a.remove_tag("location")
	print("a has tag 1 " + str(a.has_tag("location.1")))
	print(a)

test_tagged_object()