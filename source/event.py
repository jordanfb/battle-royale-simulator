"""this is a class used by the ECS to communicate between everything"""

class Event:
	def __init__(self, ID, parameters = {}):
		self.ID = ID # a string
		self.parameters = parameters # a dictionary

	def __getitem__(self, key):
		# used as a shortcut to get a parameter or the ID
		if key == "ID":
			return self.ID
		elif key in self.parameters:
			return self.parameters[key]
		else:
			return None

	def __setitem__(self, key, value):
		# used as a shortcut to set a parameter or ID
		if key == "ID":
			self.ID = value
		else:
			self.parameters[key] = value

class GetActionEvent(Event):
	# this is just so I don't have to create this every time I want to get events...
	def __init__(self):
		self.ID = "GetActions"
		self.parameters = {"actions":[]}


# def make_get_variable_event(getType, defaultValue = 0):
# 	"""getType is something like "getHealth", and this creates the default value for it as well"""
# 	return Event(getType, parameters = {"value":defaultValue})