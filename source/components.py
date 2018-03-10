class Component:
	def __init__(self, componentType, parameters, parent):
		self.componentType = componentType
		self.parent = parent # the parent entity or component
		# copy it so that multiple objects don't have linked properties
		self.parameters = {}
		for key in parameters:
			self.parameters[key] = parameters[key]

	def handle_get_actions(self, event):
		actions = self.get_actions()
		if len(actions == 0):
			return False, False
		event.parameters["actions"] += actions
		return False, True

	def get_actions(self):
		# by default there are no actions so it's an empty list
		# the actions have to give an explaination plus the text for how to do them plus what they change plus the chances of each happening plus the time to do the action...
		# that's why this is a separate function, so that it's spaced out some
		return []

	def fire_event(self, event):
		# handle the event if it can, and possibly create a child
		# return whether or not it eats the event, and whether or not it changed it
		if (event.ID == "GetActions"):
			return self.handle_get_actions(event)
		return False, False

	# def get_actions(self):
	# 	pass # get the actions possible? or is this an event. This is probably an event...

	def ensure_exists(self, key, defaultValue):
		# ensures a parameter exists
		if key not in self.parameters:
			self.parameters[key] = defaultValue

	def send_event_to_parent(self, event):
		if (self.parent != None):
			# reurn whether or not it gets recieved or changed, in case it is trying to get information from the parent for instance
			return self.parent.fire_event(event)
		return False, False

class EXAMPLECOMPONENT(Component):
	def __init__(self, parameters, parent):
		super().__init__("componentName", parameters, parent)

	def fire_event(self, event):
		# return whether or not it eats the event, and whether or not it changed it
		if (event.ID == "GetActions"):
			return self.handle_get_actions(event)
		return False, False

class Visible(Component):
	def __init__(self, parameters, parent):
		super().__init__("Visible", parameters, parent)

	def fire_event(self, event):
		if (event.ID == "GetActions"):
			return self.handle_get_actions(event)
		elif (event.ID == "Look"):
			event.parameters["visible"] = True
			return False, True
		return False, False

class Physical(Component):
	def __init__(self, parameters, parent):
		super().__init__("Physical", parameters, parent)
		self.ensure_exists("weight", 1) # weight is in grams I guess?
		self.ensure_exists("volume", 1) # in cubic cm?

	def fire_event(self, event):
		print("Physical component not implemented")
		if (event.ID == "GetActions"):
			return self.handle_get_actions(event)
		return False, False



class DisplayName(Component):
	def __init__(self, parameters, parent):
		super().__init__("DisplayName", parameters, parent)
		self.ensure_exists("spacing", "")
		self.ensure_exists("displayName", "")

	def fire_event(self, event):
		if (event.ID == "GetActions"):
			return self.handle_get_actions(event)
		elif (event.ID == "GetDisplayName"):
			if ("displayName" not in event.parameters):
				event.parameters["displayName"] = self.parameters["displayName"]
			else:
				event.parameters["displayName"] += self.parameters["spacing"] + self.parameters["displayName"]
			# doesn't eat it, yes it changes it
			return False, True
		return False, False

class DamageType(Component):
	# changes the damage type of an attack when you look for the damage caused. It will eventually at least...
	def __init__(self, parameters, parent):
		super().__init__("DamageType", parameters, parent)
		#self.ensure_exists("flamable", 0)
		self.ensure_exists("damageTypes", [])
		# a list of damage types and how much it hurts?

	def fire_event(self, event):
		# return whether or not it eats the event, and whether or not it changed it
		# if (event.ID == "")
		print("DAMAGETYPE NOT IMPLEMENTED")
		if (event.ID == "GetActions"):
			return self.handle_get_actions(event)
		return False, False

class Health(Component):
	def __init__(self, parameters, parent):
		super().__init__("Health", parameters, parent)
		self.ensure_exists("hp", 100)

	def fire_event(self, event):
		# return whether or not it eats the event, and whether or not it changed it
		if (event.ID == "GetActions"):
			return self.handle_get_actions(event)
		elif (event.ID == "TakeDamage"):
			self.parameters["hp"] -= event.parameters["amount"]
			if self.parameters["hp"] <= 0:
				killers = []
				if "killers" in event.parameters:
					killers = event.parameters["killers"]
				deathEvent = Event("Died", {"killers":killers})
				self.send_event_to_parent(deathEvent)
			return True, False # it eats it but doesn't change it
		elif (event.ID == "GetHealth"):
			event.parameters["hp"] = self.parameters["hp"]
			return False, True
		return False, False

class Inventory(Component):
	def __init__(self, parameters, parent):
		super().__init__("Inventory", parameters, parent)
		self.ensure_exists("inventory", []) # add things to the inventory I guess
		self.ensure_exists("useWeightLimit", False)
		self.ensure_exists("weightLimit", -1)

	def get_actions(self):
		# if I don't want to plan things out and have chances, then we could just add the events with a weight. But we do want to plan things out, and we want to allow the user to pick
		# something perhaps if we want someone to be able to play this. This means that we have to be able to define requirements for the action, plus the text used to describe it, plus what the action should do on what
		# {"requirements":[], "chances":[], "something":0},
		inventoryActions = [{"name":"PickUpItem", "requirements":{}, "chances":[], "results":[], "method":[]}]
		if len(self.parameters["inventory"]) > 0:
			# allow the player to drop a specific item, or drop all items
			inventoryActions += [{"name":"DropItem", "requirements":{}, "chances":[], "results":[], "method":[]}]

		
		# these have to explain a lot...
		return inventoryActions

	def fire_event(self, event):
		# return whether or not it eats the event, and whether or not it changed it
		if (event.ID == "GetActions"):
			eaten, changed = self.handle_get_actions(event)
			# then also run eaten and changed for all of the items in the inventory as well
			for item in self.parameters["inventory"]:
				itemEaten, itemChanged = item.fire_event(event)
		elif (event.ID == "PickUpItem"):
			item = event.parameters["item"]
			pickUpEvent = Event("PickedUp", {"taker":self.parent, "inventory":self})
			item.send_event(pickUpEvent)
			self.parameters["inventory"].append(item)
			return True, False

		elif (event.ID == "DropItem"):
			item = event.parameters["item"]
			dropEvent = Event("Dropped", {"dropper":self.parent, "inventory":self})
			item.send_event(dropEvent)
			self.parameters["inventory"].remove(item)
			return True, False

		elif (event.ID == "DropAllItems"):
			dropEvent = Event("Dropped", {"dropper":self.parent, "inventory":self})
			for item in self.parameters["inventory"]:
				item.send_event(dropEvent)
			self.parameters["inventory"] = []
			return True, False

		return False, False

class Static(Component):
	def __init__(self, parameters, parent):
		super().__init__("Static", parameters, parent)

	def fire_event(self, event):
		# this component is just to place on things like trees or meadows or lakes that never move so it's reasonable to assume it will always be
		# there for the brain. I think I'll need this I'm just not sure
		"""
		if (event.ID == "GetActions"):
			return self.handle_get_actions(event)
		"""
		return False, False

class Brain(Component):
	"""this is the decision making component for players and for gamemakers and whatever"""
	def __init__(self, parameters, parent):
		super().__init__("Brain", parameters, parent)

	def fire_event(self, event):
		# return whether or not it eats the event, and whether or not it changed it
		if (event.ID == "GetActions"):
			return self.handle_get_actions(event)
		return False, False

componentList = {
# start with the base component classes
# "Component":Component,
"Visible":Visible,
"Physical":Physical,
"Static":Static,

# more specific components
"DisplayName":DisplayName,
"DamageType":DamageType,
"Health":Health,
"Inventory":Inventory,
}