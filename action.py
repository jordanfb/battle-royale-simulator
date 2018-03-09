
"""
This has the action class in here which is what the components use to tell the AI what they can do
the actions have to give an explaination plus the text for how to do them plus what they change plus the chances of each happening plus the time to do the action...


things that the action can influence:
relationships
health/other stats
location


it requires certain things: for instance, an object to act upon, a player to act upon
-- check if game objects have a certain component in them as a requirement?

"""

#Action([{}, {}])


class Action:
	def __init__(self, requirements):
		self.requirements = requirements

	def evaluate(self):
		pass