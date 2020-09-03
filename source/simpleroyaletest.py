"""
This is an attempt at a simple royale test. I just wanna try a simple thing that doesn't get overengineered lol. That won't happen.


On a scale of 1-10 how scared are you (in this battle royale) when someone else is nearby? Then use that to calculate fear levels which change which tasks are more likely?
Only likely to explore when you don't know see anyone.

"""
import random


NEARBY_DISTANCE = 2
VISIBLE_DISTANCE = 3

data = """
a [Swing Sword at [p]]
"""

actions = []
items = []


class Action:
	def __init__(self, string, requirements):
		self.string = string
		self.requirements = requirements

	def can_do_action(self, person, surroundings):
		pass

	def do_action(self, person, surroundings):
		pass

class PickupAction (Action):
	def __init__(self):
		pass

	def can_do_action(self, person, world):
		# surroundings is a list of objects. We need to check to see if there are objects in that list
		pickupableObjects = [x for x in world.get_nearby_objects(person.location) if x.portable]
		return len(pickupableObjects) > 0

	def do_action(self, person, world):
		pickupableObjects = [x for x in world.get_nearby_objects(person.location) if x.portable]
		o = random.choice(pickupableObjects)
		person.inventory += [o]
		world.remove_object_from_world(o)
		print(str(person) + " picked up " + str(o))

class DropAction (Action):
	def __init__(self):
		pass

	def can_do_action(self, person, world):
		# surroundings is a list of objects. We need to check to see if there are objects in that list
		droppableObjects = [x for x in person.inventory if x.portable]
		return len(droppableObjects) > 0

	def do_action(self, person, world):
		droppableObjects = [x for x in person.inventory if x.portable]
		o = random.choice(droppableObjects)
		o.location[0] = person.location[0] # move the object to where it's dropped!
		o.location[1] = person.location[1]
		person.inventory += [o]
		world.add_object_to_world(o)
		print(str(person) + " dropped " + str(o))


class AttackAction (Action):
	def __init__(self, amount_of_damage):
		self.amount_of_damage = amount_of_damage

	def can_do_action(self, person, world):
		# surroundings is a list of objects. We need to check to see if there are objects in that list
		attackablePeople = [x for x in world.get_nearby_people(person.location) if x != person and x.health > 0]
		return len(attackablePeople) > 0

	def do_action(self, person, world):
		attackablePeople = [x for x in world.get_nearby_people(person.location) if x != person and x.health > 0]
		o = random.choice(attackablePeople)
		o.health -= self.amount_of_damage
		print(str(person) + " attacked " + str(o) + " for " + str(self.amount_of_damage) + " damage")

class FleeAction (Action):
	def __init__(self):
		pass

	def can_do_action(self, person, world):
		visiblePeople = [x for x in world.get_visible_people(person.location) if x != person and x.health > 0]
		return len(visiblePeople) > 0

	def do_action(self, person, world):
		visiblePeople = [x for x in world.get_visible_people(person.location) if x != person and x.health > 0]
		fleeVector = Vector2Int.sum_positions([person.location - p.location for p in visiblePeople]) # this is the vector pointing away from everyone
		# print(str(fleeVector))
		if (fleeVector.x == 0 and fleeVector.y == 0):
			# pick a random direction!
			while True:
				newPos = person.location + Vector2Int.get_random_direction()
				if (world.is_inside_bounds(newPos)):
					person.location = newPos
					break
			print(str(person) + " ran in a random direction")
		else:
			# flee in that direction, just normalized!
			person.location = person.location + fleeVector.clamp_to_ones()
			world.clamp_to_bounds(person.location)
			print(str(person) + " ran away from people nearby")

class ChaseAction (Action):
	def __init__(self):
		pass

	def can_do_action(self, person, world):
		visiblePeople = [x for x in world.get_visible_people(person.location) if x.location != person.location and x.health > 0]
		return len(visiblePeople) > 0

	def do_action(self, person, world):
		visiblePeople = [x for x in world.get_visible_people(person.location) if x != person and x.health > 0]
		p = random.choice(visiblePeople)
		direction = (p.location - person.location).clamp_to_ones()
		person.location = person.location + direction
		print(str(person) + " chases after " + str(p))
		# print("CLAMP THIS VECTOR THEN MOVE IN THAT DIRECTION! " + str(direction) + " from " + str(p.location - person.location))

class ExploreAction (Action):
	def __init__(self):
		pass

	def can_do_action(self, person, world):
		# explore if no one is visible!
		return len([x for x in world.get_visible_people(person.location) if x != person and x.health > 0]) <= 0 and len(world.get_visible_objects(person.location)) == 0

	def do_action(self, person, world):
		while True:
			newPos = person.location + Vector2Int.get_random_direction()
			if (world.is_inside_bounds(newPos)):
				person.location = newPos
				break
		print(str(person) + " explored in a random direction")


class CannibalismAction (Action):
	def __init__(self):
		pass

	def can_do_action(self, person, world):
		return len([x for x in world.get_nearby_people(person.location) if x != person and x.health == 0 and not x.has_been_eaten]) > 0

	def do_action(self, person, world):
		toEat = random.choice([x for x in world.get_nearby_people(person.location) if x != person and x.health == 0 and not x.has_been_eaten])
		person.health += 2
		toEat.has_been_eaten = True
		print(str(person) + " ate " + str(toEat))


class MoveTowardsRandomPersonByChance (Action):
	def __init__(self):
		pass # this class is here to basically make them eventually move towards each other so that the games aren't infinite :P

	def can_do_action(self, person, world):
		# explore if no one is visible!
		return len(world.get_visible_people(person.location)) <= 1 and len(world.get_visible_objects(person.location)) == 0

	def do_action(self, person, world):
		allPeople = [x for x in world.people if x != person]
		p = random.choice(allPeople)
		direction = (p.location - person.location).clamp_to_ones()
		person.location = person.location + direction
		print(str(person) + " randomly moved towards " + str(p))


class Item:
	def __init__(self, string):
		self.portable = True
		self.location = Vector2Int(0, 0)
		self.actions = []


class Person:
	def __init__(self, name):
		self.name = name
		self.health = 100
		self.inventory = [] # full of items
		self.location = Vector2Int(0, 0)
		self.points_to_investigate = [] # these could be smoke visible from campfires or last seen locations of people or interesting objects! They should slowly decay over time
		self.has_been_eaten = False
		self.display_letter = "#"

	def get_actions(self, world):
		# get a list of all possible actions from your inventory!
		actions = []

		# now check all the object actions
		for o in self.inventory:
			for a in o.actions:
				if a.can_do_action(self, world):
					actions += [a]
		# now check all the default actions that everyone can do!
		for a in world.defaultPeopleActions:
			if a.can_do_action(self, world):
				actions += [a]

		return actions

	def take_turn(self, world):
		actions = self.get_actions(world)
		if len(actions) == 0:
			return False
		else:
			# take an action!
			a = random.choice(actions)
			a.do_action(self, world)
			return True

	def __repl__(self):
		return str(self.name) + " at " + str(self.health) + " health at " + str(self.location)

	def __str__(self):
		return self.__repl__()


class World:
	def __init__(self):
		self.npcs = []
		self.people = []
		self.objects = []
		self.dimensions = [11, 11]
		self.defaultPeopleActions = []
		self.unique_identifiers = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

	def get_nearby_objects(self, location):
		return self.get_objects_within_range(location, NEARBY_DISTANCE)

	def get_nearby_people(self, location):
		return self.get_people_within_range(location, NEARBY_DISTANCE)

	def get_visible_objects(self, location):
		return self.get_objects_within_range(location, VISIBLE_DISTANCE)

	def get_visible_people(self, location):
		return self.get_people_within_range(location, VISIBLE_DISTANCE)

	def is_inside_bounds(self, position):
		return position.x >= 0 and position.y >= 0 and position.x <= self.dimensions[0] and position.y <= self.dimensions[1]

	def clamp_to_bounds(self, position):
		position.x = min(self.dimensions[0], max(position.x, 0))
		position.y = min(self.dimensions[1], max(position.y, 0))

	def get_objects_within_range(self, location, distance):
		nearby = []
		for o in self.objects:
			if location.get_distance(o.location) <= distance:
				nearby += [o]
		return nearby

	def get_people_within_range(self, location, distance):
		nearby = []
		for o in self.npcs:
			if location.get_distance(o.location) <= distance:
				nearby += [o]
		for o in self.people:
			if location.get_distance(o.location) <= distance:
				nearby += [o]
		return nearby

	def get_random_coords(self):
		return Vector2Int(random.randint(1, self.dimensions[0]), random.randint(1, self.dimensions[1]))

	def get_center_coords(self):
		c = Vector2Int(int(self.dimensions[0]/2), int(self.dimensions[1]/2))
		return c

	def add_object_to_world(self, o):
		self.objects += [o]

	def remove_object_from_world(self, o):
		self.objects.remove(o)

	def get_all_positions(self):
		# loop through all the objects and add the positions of things to a dictionary list so we know what is where!
		pos = {}
		for p in self.people:
			loc = p.location.to_tuple()
			if loc not in pos:
				pos[loc] = []
			pos[loc] += [p]
		return pos


	def print_world(self):
		# this is my current attempt at drawing the world tile by tile!
		y_scale = 2
		x_scale = 2

		positions = self.get_all_positions()

		for p in self.people:
			print(str(p) + " => " + str(p.display_letter))
		for i in range(y_scale):
			print("+"*x_scale + "-" *(self.dimensions[0]+1)*x_scale + "+"*x_scale)
		for y in range(self.dimensions[1]+1):
			for i in range(y_scale):
				print("|"*x_scale, end = "")
				for x in range(self.dimensions[0]+1):
					pos = (x, y)
					for j in range(x_scale):
						if pos in positions:
							# then we have something in this tile!
							t = positions[pos][0]
							positions[pos] = positions[pos][1:] # remove the first item from the list now!
							if len(positions[pos]) == 0:
								del positions[pos] # remove the list entirely so we know there are no more items left!
							print(t.display_letter, end="")
						else:
							if x % 2 == y % 2:
								print(" ", end="")
							else:
								print(".", end = "")
				print("|"*x_scale) # new line
		for i in range(y_scale):
			print("+"*x_scale + "-" *(self.dimensions[0]+1)*x_scale + "+"*x_scale)

	def randomize_position(self, obj):
		obj.location = self.get_random_coords()

	def randomize_all_object_positions(self):
		for o in self.objects:
			self.randomize_position(o)

	def initialize_people_positions(self):
		for p in self.people:
			p.location = self.get_center_coords()

	def get_all_players_as_string(self):
		x = [str(p) for p in self.people]
		return ", ".join(x)

	def assign_all_players_unique_display_letters(self):
		random.shuffle(self.people)
		for p in self.people:
			self.assign_player_unique_display_letter(p)

	def assign_player_unique_display_letter(self, o):
		preferredName = o.name
		while len(preferredName) > 0:
			if (preferredName[0].upper() in self.unique_identifiers):
				o.display_letter = preferredName[0].upper()
				self.unique_identifiers = self.unique_identifiers.replace(o.display_letter, "")
				return
			elif (preferredName[0].lower() in self.unique_identifiers):
				o.display_letter = preferredName[0].lower()
				self.unique_identifiers = self.unique_identifiers.replace(o.display_letter, "")
				return
			else:
				preferredName = preferredName[1:]
		# there are no letters in the name that haven't been taken so just assign a random letter...
		o.display_letter = self.unique_identifiers[0]
		self.unique_identifiers = self.unique_identifiers[1:]

	def take_turn(self):
		# shuffle the order of all the characters:
		random.shuffle(self.npcs)
		random.shuffle(self.people)


		# first evaluate all the environmental effects
		something_did_something = False
		for n in self.npcs:
			if n.health <= 0:
				continue # dead things can't do things!
			something_did_something |= n.take_turn(self)

		# then evaluate the people
		for p in self.people:
			if p.health <= 0:
				continue # dead things can't do things!
			something_did_something |= p.take_turn(self)

		# check if we have a winner!
		alive_players = []
		for p in self.people:
			if p.health > 0:
				alive_players += [p]

		if len(alive_players) == 0:
			# then we have a tie!
			print("\nWe have a tie!")
			print(self.get_all_players_as_string())
			return False # simulation ended
		elif len(alive_players) == 1:
			print("\nWe have a winner! " + str(alive_players[0]))
			print(self.get_all_players_as_string())
			return False # simulation ended
		else:
			return something_did_something # more turns


def parse_objects(mega_string, world):
	# parses data into a bunch of objects I guess?
	lines = mega_string.split("\n")
	lines = [l.strip() for l in lines]
	for l in lines:
		pass # parse each line!
		if len(l) <= 1:
			continue
		parse_line(l, world)

def parse_line(line, world):
	pass


class Vector2Int:
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def get_distance(locA, locB):
		d = abs(locA[0] - locB[0])
		d += abs(locA[1] - locB[1])
		return d

	def to_tuple(self):
		return (self.x, self.y)

	def sum_positions(positions):
		d = Vector2Int(0, 0)
		for p in positions:
			d.x += p.x
			d.y += p.y
		return d

	def get_random_direction():
		x = random.randint(-1, 1)
		y = random.randint(-1, 1)
		while x == 0 and y == 0:
			x = random.randint(-1, 1)
			y = random.randint(-1, 1)
		return Vector2Int(x, y)

	def __getitem__(self, key):
		if key == 0:
			return self.x
		elif key == 1:
			return self.y

	def __setitem__(self, key, value):
		if key == 0:
			self.x = value
			return self.x
		elif key == 1:
			self.y = value
			return self.y

	def __add__(self, other):
		if type(other) == Vector2Int:
			return Vector2Int(self.x + other.x, self.y + other.y)

	def __sub__(self, other):
		if type(other) == Vector2Int:
			return Vector2Int(self.x - other.x, self.y - other.y)

	def __neg__(self):
		return Vector2Int(-self.x, -self.y)

	def __abs__(self):
		return Vector2Int(abs(self.x), abs(self.y))

	def __eq__(self, other):
		if isinstance(other, Vector2Int):
			return self.x == other.x and self.y == other.y
		return False # just assume it's not the same then

	def block_magnitude(self):
		return abs(self.x) + abs(self.y)

	def __str__(self):
		return "(" + str(self.x) + ", " + str(self.y) + ")"

	def __repl__(self):
		return str(self)

	def clamp_to_ones(self):
		new_x = round(self.x)
		new_y = round(self.y)
		return Vector2Int(new_x, new_y)



if __name__ == "__main__":
	# then run a test simulation I guess?
	w = World()
	parse_objects(data, w)

	w.defaultPeopleActions += [PickupAction(), DropAction(), AttackAction(1), FleeAction(), ChaseAction(), ExploreAction(), MoveTowardsRandomPersonByChance(), CannibalismAction()]


	w.people += [Person("Jordan")]
	w.people += [Person("Schuyler")]
	w.people += [Person("Jenna")]
	w.people += [Person("Joe")]

	# get ready to start the match
	w.initialize_people_positions()
	w.randomize_all_object_positions()
	w.assign_all_players_unique_display_letters()

	took_turn = True
	t = 0
	while took_turn:
		print("\n\n\nTurn " + str(t))
		print(w.get_all_players_as_string())
		w.print_world()
		print()
		took_turn = w.take_turn()
		t += 1
	w.print_world()
	# the simulation is over!
