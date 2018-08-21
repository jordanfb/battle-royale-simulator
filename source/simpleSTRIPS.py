"""
What is this?
some creatures for an LED light wall?
AI for hunger games?
AI planning for Non-Orbital?
Writing thing?
Story generation?




Simplify GOAP by having generic actions that are "use ranged weapon" which has a fitness evaluator that takes the best of all the weapons for the character rather than having a ton of different actions.
Sticks can only be fashioned with some skill I guess. Still not sure if a planner is the best.
Counter planners can involve building simulated models of the other AI then Alpha-Beta planning with them. How do we ab plan with a GOAP? What is the best action?
Obviously the action that makes the most sense for their state and the world state. Then people can choose how pessemistic their model is for everyone, which would make them more likely to be meaner or something.
It would be kinda nice to have an actual python install lol.

Let's start with a simple set of actions before adding generalized stuff as well.
How do we do that?
Super basic items allow for actions. Everything has a deep copy function for planning.
No. This is not the way. Every AI has a set of actions they can do on associated items. That way we can search backwards.
First things first forget opponent modeling. Worst case scenario we can just replan every time.


Have people done opponent modeling with backwards searching GOAP?
Also, can you sniff out a MAC address for a plane network then spoof your own then connect as them? Or does that not work?



currently working on prereqs, then results, then goals, then pathing, then see what happens probably?
Things learned:
Need a way to represent goals that can be greater than. You can have greater than 10 money as long as you have at least 10.
Need a way to randomize things
Need a way to influence choices based on personality (this can also be used for counter-planning, by having scared people assign a higher probability for someone finding and attacking you)
Need a way to generalize things (pick up ITEM instead of pick up stick)

Currently ignoring all of those things and working on reverse planning to make it actually find a nicely efficient plan
Basically if the action has a change that influences something that is not satisfied by the world state it should add it to the stack. You never want to do actions that are unrelated to
the current unstatisfied world state because they aren't useful towards making your plan actually a thing. Is it possible to counter-plan against another AI using reverse planning? Maybe not.
"""


class StripsWorld:
	def __init__(self, stateIn=None):
		self.state = {} # a dictionary of bools
		if (stateIn):
			for key in stateIn:
				self.state[key] = stateIn[key]

	def clone(self):
		newWorld = StripsWorld(self.state)
		return newWorld

	def set_flag(self, key, value):
		# return if it changed something or not
		change = self.state[key] == value
		self.state[key] = value
		return change

	def get_flag(self, key):
		if key in self.state:
			return self.state[key]
		else:
			return None

	def contains_flag(self, key):
		return key in self.state

	def __str__(self):
		return str(self.state)

	def __repr__(self):
		return str(self)

	def __eq__(self, other):
		return self.compare_states(other) == 0

	def __ge__(self, other):
		# this is used to compare states. If this state is greater than or equal to the other state then this state contains that state
		# (i.e. if this is a goal state you want this to be greater than the current state)
		for our_key in self.state:
			# For now, let's require that the other state have keys that are equal to this and not bother with actual numbers since __ge__ doesn't support that anyways
			# we could do things like require >10 money but that seems a pain since it requires defining how to compare each key of the world state and what is better than
			# what, which may change from planner to planner
			if (our_key not in other.state):
				return False
			elif self.state[our_key] != other.state[our_key]:
				return False
		return True

	def __hash__(self):
		return self.simple_hash()

	def simple_hash(self):
		# go through the keys alphabetically and combine them and values as strings
		keys = list(self.state.keys())
		keys.sort()
		s = ""
		for key in keys:
			s += str(key) + str(self.state[key])
		return hash(s)

	def compare_states(self, other, check_all_changes = False):
		# return how similar they are I guess. For now we'll just do whether they're equal or not. I may want to change it to compare numbers.
		different = 0
		for our_key in self.state:
			if our_key in other.state:
				if (type(self.state[our_key]) == int or type(self.state[our_key]) == float) and (type(other.state[our_key]) == int or type(other.state[our_key]) == float):
					# compare numbers
					different += abs(self.state[our_key] - other.state[our_key])
				else:
					different += (self.state[our_key] != other.state[our_key])
			else:
				different += 1
		if (check_all_changes):
			for their_key in other.state:
				if their_key not in self.state:
					different += 1
		return different

class SimpleSTRIPSPrereq:
	def __init__(self, name, key, comparison, value):
		# this is used to check prereqs for actions.
		self.name = name
		self.key = key
		self.comparison = comparison
		self.value = value

	def is_satisfied(self, worldstate):
		# returns whether or not it is valid in this world state by evaluating the comparison
		state_value = worldstate.get_flag(self.key)
		if (self.comparison == ">"):
			return state_value > self.value
		elif self.comparison == ">=":
			return state_value >= self.value
		elif self.comparison == "<":
			return state_value < self.value
		elif self.comparison == "<=":
			return state_value <= self.value
		elif self.comparison == "!=":
			return state_value != self.value
		elif self.comparison == "==":
			return state_value == self.value # add one difference if they're not equal

	def __repr__(self):
		return str(self)

	def __str__(self):
		return "PREREQ: " + str(self.name) + ": " + str(self.key) + " " + str(self.comparison) + " " + str(self.value)

class STRIPSEqualPrereq (SimpleSTRIPSPrereq):
	def __init__(self, name, key, value):
		super().__init__(name, key, "==", value)

class SimpleSTRIPSChange:
	# a change made by an action. Should be able to apply and reverse yourself for use with forwards and backwards planning.
	def __init__(self, name, key, action, value):
		self.name = name
		self.key = key
		self.action = action
		self.value = value

	def apply(self, state):
		if self.action == "=":
			state.set_flag(self.key, self.value)
		elif self.action == "+=":
			state.set_flag(self.key, state.get_flag(self.key)+self.value)
		elif self.action == "-=":
			state.set_flag(self.key, state.get_flag(self.key)-self.value)

	def changes_something_in_world_state(self, state):
		# this checks to see if the change affects something in the world state already. This is used for backwards planning
		return state.contains_flag(self.key)

	def __repr__(self):
		return str(self)

	def __str__(self):
		return "CHANGE: " + str(self.name) + str(self.key) + " " + str(self.action) + " " + str(self.value)

class SimpleSTRIPSAction:
	def __init__(self, name, cost, prereqs, changes):
		self.name = name
		self.cost = cost
		self.prereqs = prereqs
		self.changes = changes

	def can_be_done(self, state):
		#return whether it can be done in this world state
		for prereq in self.prereqs:
			#print(prereq.prereq_passes(state))
			if not prereq.is_satisfied(state):
				return False
		return True

	def do_action(self, state):
		# apply the state to the world going forwards in time (apply all of the changes)
		for change in self.changes:
			change.apply(state)

	def apply(self, state):
		self.do_action(state)

	def reverse_action(self, state):
		# do the opposite of action to the world (i.e. go backwards) for backwards planning
		print("REVERSE ACTION ISN'T IMPLEMENTED")
		pass

	def changes_something_in_world_state(self, state):
		# this checks to see if the changes affect something in the world state already. This is used to see if we should try this path out for backwards planning
		for change in self.changes:
			# check to see if the change changes something in the world state.
			if change.changes_something_in_world_state(state):
				return True
		return False

	def __repr__(self):
		return self.full_str()

	def __str__(self):
		return "ACTION " + str(self.name)

	def full_str(self):
		out = "ACTION " + str(self.name) + "\nCost: " + str(self.cost)
		out += "\nPrereqs:\n" + "\n".join([str(p) for p in self.prereqs])
		out += "\nChanges:\n" + "\n".join([str(c) for c in self.changes])
		return out

class SimpleSTRIPSPlanner:
	def __init__(self, name, startingstate, goalstate, actions):
		self.name = name
		self.goalstate = goalstate
		self.startingstate = startingstate
		self.actions = actions

	def forward_plan(self, max_depth = 50000):
		# forward plan, returning a list of actions that it would take
		if (self.goalstate >= self.startingstate):
			return True, [], self.startingstate
		actions = []
		frontier = [(self.startingstate.clone(), self.goalstate.compare_states(self.startingstate), [])]
		i = 0
		tried_plans = 1
		visited = {hash(self.startingstate)} # this is annoying. Perhaps a hash would work best rather than comparing an ever increasing number of world states? For now just limit the loops
		# the frontier is the list of worldstates, difference from the goal state, and actions to get there. Eventually I should sort this based on difference from the goalstate
		while len(frontier) > 0:
			i += 1
			current_state = frontier[0]
			frontier = frontier[1:]
			possible_actions = [action for action in self.actions if action.can_be_done(current_state[0])]
			for action in possible_actions:
				# do the action and add the new action to the frontier. For now just do a BFS. This will likely need to change for performance's sake
				clone = current_state[0].clone()
				tried_plans += 1 # keeping track of how many paths it walked down
				action.do_action(clone)
				h = hash(clone)
				if h not in visited:
					visited.add(h)
					action_list_clone = [a for a in current_state[2]] + [action]
					frontier += [[clone, self.goalstate.compare_states(clone), action_list_clone]]
					if (self.goalstate >= clone):
						print("NUMBER OF TRIED PLANS: " + str(tried_plans))
						print("NUMBER OF PLANS ON FRONTIER: " + str(len(frontier)))
						return True, action_list_clone, clone
				# otherwise it's already visted that state and tried everything from there. This should prevent obvious infinite loops
			if i > max_depth:
				break # didn't make it. :(
		return False, [], self.startingstate # first is whether or not you got to the goal the second is the list of actions to take

	def plan_string(self, plan):
		out = "Plan by " + str(self.name) + "\n"
		out += "Starting State " + str(self.startingstate) + "\n"
		testWorldState = self.startingstate.clone()
		for action in plan:
			if (not action.can_be_done(testWorldState)):
				out += "OH DEAR THIS ACTION CAN'T BE DONE:\n"
			action.apply(testWorldState)
			out += str(action) + " : " + str(testWorldState) + "\n"
		#out += "\n".join([str(action) for action in plan]) + "\n"
		out += "Hopefully ending at goal state: " + str(self.goalstate)
		return out


if __name__ == "__main__":
	# then run a simple strips test.
	# print out the plan it creates in this world
	startingKeys = {"logsInInventory":0, "sticksInInventory":0, "hasAxe":False, "characterLocation":"hut", "moneyInInventory":0}
	startingWorld = StripsWorld(startingKeys)
	print(startingWorld)
	goalKeys = {"moneyInInventory":10}
	goalWorld = StripsWorld(goalKeys)
	print(goalWorld)
	print("Has goal already succeded? " + str(goalWorld >= startingWorld))

	changes = {"setlocation_woods":SimpleSTRIPSChange("Go to woods", "characterLocation", "=", "woods"), \
				"setlocation_hut":SimpleSTRIPSChange("Go to hut", "characterLocation", "=", "hut"),\
				"setlocation_store":SimpleSTRIPSChange("Go to store", "characterLocation", "=", "store")}

	prereqs = {"isat_woods":STRIPSEqualPrereq("Is at woods", "characterLocation", "woods"),\
				"isat_hut":STRIPSEqualPrereq("Is at hut", "characterLocation",  "hut"),\
				"isat_store":STRIPSEqualPrereq("Is at store", "characterLocation",  "store")}

	actions = []
	# SimpleSTRIPSAction(name cost prereqs changes)
	# SimpleSTRIPSChange(name key action value)
	# SimpleSTRIPSPrereq(name key comparison value)
	#actions.append(SimpleSTRIPSAction("Free Money", 0, [], [SimpleSTRIPSChange("Increase money by one", "moneyInInventory", "+=", 1)]))
	actions.append(SimpleSTRIPSAction("Throw Away Money", 0, [], [SimpleSTRIPSChange("Decrease money by one", "moneyInInventory", "-=", 1)]))
	actions.append(SimpleSTRIPSAction("Hut To Woods", 0, [prereqs["isat_hut"]], [changes["setlocation_woods"]]))
	actions.append(SimpleSTRIPSAction("Woods To Hut", 0, [prereqs["isat_woods"]], [changes["setlocation_hut"]]))
	actions.append(SimpleSTRIPSAction("Hut To Store", 0, [prereqs["isat_hut"]], [changes["setlocation_store"]]))
	actions.append(SimpleSTRIPSAction("Store To Hut", 0, [prereqs["isat_store"]], [changes["setlocation_hut"]]))
	actions.append(SimpleSTRIPSAction("Gather Sticks", 0, [prereqs["isat_woods"]], [SimpleSTRIPSChange("Add Stick to inventory", "sticksInInventory", "+=", 1)]))
	actions.append(SimpleSTRIPSAction("Sell stick", 0,
			[prereqs["isat_store"], SimpleSTRIPSPrereq("Has a stick", "sticksInInventory", ">", 0)], \
			[SimpleSTRIPSChange("Remove Stick from inventory", "sticksInInventory", "-=", 1), SimpleSTRIPSChange("Add .5 money to inventory", "moneyInInventory", "+=", .5)]))
	actions.append(SimpleSTRIPSAction("Sell log", 0,
			[prereqs["isat_store"], SimpleSTRIPSPrereq("Has a log", "logsInInventory", ">", 0)], \
			[SimpleSTRIPSChange("Remove log from inventory", "logsInInventory", "-=", 1),SimpleSTRIPSChange("Add 1 money to inventory", "moneyInInventory", "+=", 1)]))
	actions.append(SimpleSTRIPSAction("Buy axe", 0,
			[prereqs["isat_store"], SimpleSTRIPSPrereq("Has 2 money", "moneyInInventory", ">=", 2)], \
			[SimpleSTRIPSChange("Remove money from inventory", "moneyInInventory", "-=", 2), SimpleSTRIPSChange("Add axe to inventory", "hasAxe", "=", True)]))
	actions.append(SimpleSTRIPSAction("Chop down tree", 0,
			[prereqs["isat_woods"], SimpleSTRIPSPrereq("Has axe", "hasAxe", "==", True)], \
			[SimpleSTRIPSChange("Add 2 logs to inventory", "logsInInventory", "+=", 5)]))
	#actions.append(SimpleSTRIPSAction("Magically get money", 0, [], [SimpleSTRIPSChange("Add 1 money to inventory", "moneyInInventory", "+=", 1)]))

	planner = SimpleSTRIPSPlanner("Woodcutter", startingWorld, goalWorld, actions)
	success, plan, final_state = planner.forward_plan()
	print(planner.plan_string(plan))
	print("Final State: " + str(final_state))
	print("Did it make it? " + str(success))
	#print("")
	#print("\n\n".join([s.full_str() for s in plan]))