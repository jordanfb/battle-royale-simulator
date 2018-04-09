import json
from components import *
import sys
import event
import formulaparser
import random

class GameObject:
	"""This is representative of physical objects, they have attributes, and they have actions
	that they can do. They also have descriptions etc. These things are loaded from a text file."""
	def __init__(self):
		self.id = -1
		self.world = None
		self.attributes = {"id":self.id, "world":self.world}

	def update(self, dt):
		"""GameObjects by default don't have agency but they may still do things..."""
		pass

	def set_world_info(self, id, world):
		self.id = id
		self.attributes["id"] = id
		self.world = world
		self.attribuets["world"] = world

	def get_attribute(self, attribute):
		if attribute not in self.attributes:
			return None
		return self.attributes[attribute]

class Intelligence:
	"""This is a class representing an intelligence which decides what actions to take.
	For now this will likely be a simple utility AI"""
	def __init__(self):
		self.id = -1
		self.world = None
		self.attributes = {"id":self.id, "world":self.world}

	def set_world_info(self, id, world):
		self.id = id
		self.attributes["id"] = id
		self.world = world
		self.attribuets["world"] = world

	def update(self, dt):
		# get actions from self
		# get actions from surrounding world
		# choose action
		# tell world what action you're doing.
		pass

	def get_attribute(self, attribute):
		if attribute not in self.attributes:
			return None
		return self.attributes[attribute]

class World:
	"""This is the class that holds all of the objects in it and handles updating them.
	This is then used by whatever class deals with the output and messenger to deal with updating
	everyone else."""
	def __init__(self):
		self.current_id = 1 # what to use for the next thing you create in the world
		self.gameObjects = []
		self.intelligences = []
		self.attributes = {"id":0, "world":self}

	def update(self, dt):
		"""sort list of objects randomly then update everything in this world"""
		random.shuffle(self.gameObjects)
		for item in self.gameObjects:
			description = item.update(dt)

	def add_to_world(self, thing):
		"""add this to the world"""
		thing.set_world_info(self.current_id, self)
		self.gameObjects.append(thing)
		self.current_id += 1

	def get_attribute(self, attribute):
		if attribute not in self.attributes:
			return None
		return self.attributes[attribute]