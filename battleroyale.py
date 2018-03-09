import json
from components import *
import sys

class Event:
	def __init__(self, ID, parameters = {}):
		self.ID = ID # a string
		self.parameters = parameters # a dictionary

class GetActionEvent(Event):
	# this is just so I don't have to create this every time I want to get events...
	def __init__(self):
		self.ID = "GetActions"
		self.parameters = {"actions":[]}


class Entity:
	def __init__(self, world):
		self.components = []
		self.world = world # the world is probably used by most of the components that have to do things in the world, like eyes, or inventory, or attacking nearby things,

	def add_component(component):
		self.components.append(component)
		# possibly do something more like register what components need to be updated or something...

	def remove_component(component):
		self.components.remove(component)
		# possibly do more, but hey...

	def fire_event(event):
		# handle the event or distribute it to your children
		# return whether or not it eats the event
		hasBeenChanged = False
		for component in component:
			eaten, changed = component.fire_event(event)
			hasBeenChanged = hasBeenChanged or changed
			if (eaten):
				return True, hasBeenChanged
		# we may or may not have it so that entities eat events at the end no matter what, but for now it wasn't eaten so it returns false
		# I think it should return false, because if an event gets sent to this entity from another it will return back to that entity,
		# if the world sends an event to everything or something like that though, it will continue until it's eaten or nothing takes it
		return False, hasBeenChanged


class Factory:
	# builds objects from the blueprints file out of components
	def __init__(self, filename = "blueprints.txt"):
		# load blueprints
		self.filename = filename
		self.blueprints = {} # this gets overwritten by load_blueprints
		self.load_blueprints(self.filename)

	def create(self, blueprint):
		# return the created blueprint
		if blueprint not in self.blueprints:
			print("ERROR: blueprint '" + blueprint + "' not found")
			sys.exit(0)
		blueprint = self.blueprints[blueprint]
		parts = blueprint["parts"]
		# then create an entity and add the various components
		entity = Entity()
		for part in parts:
			partName = part[0]
			partParameters = part[1]
			if (partName not in componentList.keys()):
				print("ERROR: part '" + partName + "' not found")
				sys.exit(0)
			# otherwise create the part and let it set the parameters
			createdPart = componentList[partName](partName, partParameters, entity) # the entity is the parent
			# then attach the part
			entity.add_component(createdPart)
		return entity

	def load_blueprints(self, filename):
		file = open(filename)
		text = file.read()
		try:
			self.blueprints = json.loads(text)
		except:
			print("ERROR: blueprints failed to load correctly")
		file.close()


class World:
	def __init__(self):
		# keeps track of time, and where things are located, and conditions, and 
		pass

	def fire_event(event):
		# this is a bastard son, it will fire the event to everything in the world I guess? But it can also recieve events like requests for what time it is and how bright it is in a certain location...
		# eyes and ears use this event to request information about what's around them I guess...
		pass



class Games:
	# this is the main class that handles the games I guess. This stores the world state and everything in it and whatever...
	def __init__(self):
		self.gameObjectFactory = Factory()

	def update(self, time):
		# update everything that updates itself in the world I guess? brains, eyes, ears, touch, world time
		pass