
"""
This has the action class in here which is what the components use to tell the AI what they can do
the actions have to give an explaination plus the text for how to do them plus what they change plus the chances of each happening plus the time to do the action...


things that the action can influence:
relationships
health/other stats
location


it requires certain things: for instance, an object to act upon, a player to act upon
-- check if game objects have a certain component in them as a requirement?


requirements are this:
Action: Attack object via Melee
needs 2 gameobjects
A with health, physics, visible, and distance < 5 # to use as a weapon
B which is in self.hands. To use as a weapon -> the stats of this change the outputs
results:
A.getCompontent("health").parameters["hp"] -= B.UseAsMeleeWeaponGetDamage()# this may be an average damage dealt, because there may be skills/randomizing involved
B is damaged by however much it says it is when used as a melee weapon
time += 5 seconds

Action: Pick up item from ground
needs 2 gameobjects
A with empty hand (A is probably the brain's gameobject (this will probably work out because the brain gets this action from the hand itself))
B item nearby on ground with physics object and visible and with a small enough volume and weight that it's carryable, B not equal to A
results:
A has item in Hand ----- note how do I use this in the planning? Is this just a prereq for certain things? Probably, actually the above should have this as a prereq
B is not on ground
time += 3 seconds

Action: Drop item to ground:
A with hand (same deal as with pick up item from ground, the hand gives this action to the brain that is trying to use it, so it works out)
B item in that hand -- so somehow the brain also has to know what's in its inventory
results:
B is not in hand
A has n-1 items that satisfy B in hand
time += 1 second

Action put item into inventory:
A with hand
B item in hand, item not equal to A (can't put a bag into itself)
C inventory nearby to put item into
result:
B is not in hand
B is in inventory C
time += 5 seconds

Action take item from inventory:
A = empty hand controllable by the brain
B inventory accessable by A
C item in inventory
result:
C not in inventory
C in hand
A's hand is not empty
time += 5 seconds

so now by default you can attack with melee using your fists, but you can also pick up a nearby item on the ground, and can store it in your bag.
And then take it out of your bag and put it on the ground

test brain goal:
no items on the ground nearby -- the way to do this is to see that pick up item from ground has the side effect of removing something from the floor, which
is closer to your goal by euclidian distance, thus do it, using the pathing algorithm.

What there has to be is a repository of items nearby that you have sensed using feeling, hearing, and seeing. You can try to apply any action onto those
items, resulting in the results or whatever

There also has to be a section of items that are in your body's inventory -- a backpack or sheathe or whatever, and a list of items that are in your hands I guess.
You can't swing a sword that is in your backpack or your sheathe or hooked onto your belt, you have to take it out first.

Thus, for requirements there have to be different stages:
A = item in hands
B = item in total player inventory -- including hands
C = item not in hands -- I don't know if I need a general thing like this, since inventories will give the option to take that item out of it
C.5 = item in player inventory -- this is for clothing, bags, sheeths, items strapped onto you, etc. Player takes off the coat. Player takes off the backpack.
D = item in specific inventory? This is usefull for bags etc., because they give the option: take item out of bag
# E = item visible -- allows the player to go over to it and pick it up? I don't think this is neccessary, since nearby will include this.
F = item nearby -- allows the player to go over to it and do something to it? These are items seen, heard, and felt added by the sense components


"""

#Action([{}, {}])

import sys


class Action:
	def __init__(self, requiredGameobjects, displayTextStuff):
		# requiredGameobjects is a list of lists of gameobject requirements, each element in that list represents a gameobject that is needed for the
		# action, they may or may not be unique (unless they have the requirement that they be unique, then they won't be guarenteed to be)
		self.requiredGameobjects = requiredGameobjects
		self.numGameobjectsNeeded = len(requiredGameobjects)
		# displayTextStuff is the information needed to describe what is happening. This may or may not be needed (perhaps it's used for an inner monologue?)
		# because the displaytext may happen in the systems when they recieve the events that are occuring
		self.displayTextStuff = displayTextStuff

	def evaluate_requirements(self, gameobjects):
		#gameobjects is a list of game objects that it's trying to evaluate for working.
		# this returns whether or not it worked, and the index of which gameobject failed
		if len(gameobjects) != self.numGameobjectsNeeded:
			print("Passed in the wrong number of gameobjects for requiremnt")
			print("Needed: " + str(self.numGameobjectsNeeded) + " Gave: " + str(len(gameobjects)))
			sys.exit(0) # hopefully this will never happen
		for i in range(self.numGameobjectsNeeded):
			"""
			requirement examples
			{ type:gameobject_with_components, parameters:{requiredComponents:["Health", "Physics", "Visible"]} }
			{type:distance, parameters: {origin:parent, maxDistance:value, minDistance: value}} # if max or min distance doesn't exist don't check that one

			"""
			requirements = self.requiredGameobjects[i]
			testsubject = gameobjects[i]
			if testsubject == None:
				print("ERROR: gameobject tested for Action is None")
				# I'm going to let this one slide even though I'm printing an error, because A hopefully this will never happen, and B, it shouldn't
				# destroy anything since we caught it. This is recoverable
				print("Requirement: " + str(requirement)) # this is just to try to give context as to where it was
				return False, i # if it doesn't exist, it doesn't fit the case. This is just for error checking
			for requirement in gameobjectNeeded:
				# check the testsubject to see if it fits that requirement. If it doesn't, return false
				requirementType = requirement["type"]
				inverted = False
				if "inverted" in requirement:
					inverted = requirement["inverted"] # so that you can require it not have a certain component. Like a brain for example.
				
				if requirementType == "inInventory":
					# check if the item is being stored in an inventory, with the ability to limit what types of inventory we check
					# this seems to be a simple way to prune the possibilities quickly from the earlier side, but for now just check it
					getItemParameters = {"items":[]}
					if "inventoryConstraint" in requirement:
						# constrain what types of inventory are accepted, for instance, only in manipulators, only in bag, 
						# in bag or on body or in hands, nearby, ever seen/have a vague idea where it is,
						#getItemParameters["inventoryTypes":["manipulators", "bag", "body", "nearby", "visible"]]
						getItemParameters["inventoryConstraint"] = requirement["inventoryConstraint"]
						# the inventories that recieve this event have to deal with it.
					getItemParameters["recursive"] = True # by default this goes recursively for inventories inside of inventories
					if "recursive" in requirement:
						getItemParameters["recursive"] = requirement["recursive"] # by default this should be true, but occasionally we may want this...
					getItemEvent = Event("getItemsInInventory", getItemParameters) # manipulators will add the items they are holding to that list and return it
					# now we have to find what the manipulators have to belong to.
					inventoryParent = self.getRequirementReferencedGameobject(requirement, "InventoryParent", gameobjects)
					# the parent should not be None (otherwise it would error), so we can send it the event and try to get whether or not we can run this on this game obejct
					eaten, changed = inventoryParent.fire_event(getItemEvent)
					if changed:
						# then check if this item is one of the items being held in the parent's inventory spaces
						items = getItemEvent.parameters["items"]
						if testsubject in items:
							if inverted:
								# don't want item in inventory:
								return False, i
							else:
								continue # check the next requirement since this one works...
					# the parent isn't containing any items (or not containing the correct one), so this one can't be contained by it
					if inverted:
						# if inverted then you don't want to be containing it
						continue
					else:
						# if not inverted then you want to be containing it, sorry, you fail
						return False, i
				elif requirementType == "hasComponents":
					# then check to see if the gameobject has components of that type
					# this makes sense to have as a function of the gameobject class actually, so it just calls that on the testsubject
					if inverted == testsubject.hasComponents(components):
						# then it's wrong, and should return false
						return False, i
					# otherwise continue
					continue
				elif requirementType == "inventoryHasSpaceForItem":
					# this is used to check if an inventory has space for the item you're trying to put into it
					# eventually I'll add inventory size limits and carrying capacity. For now I'll probably just return true? I guess?
					# it uses a lot of similar code to inInventory
					# arguably this needs an inventory component, but that should probably be the first thign? I guess not, because this
					# just returns false by default unless the inventory says it has space...
					item = self.getRequirementReferencedGameobject(requirement, "Item", gameobjects)
					inventoryParent = self.getRequirementReferencedGameobject(requirement, "InventoryParent", gameobjects)
					getInventorySpaceParameters = {"hasSpace":False, "item":item}
					getInventorySpaceEvent = Event("hasSpaceForItem", getInventorySpaceParameters)
					eaten, changed = inventoryParent.fire_event(getInventorySpaceEvent)
					if changed:
						# check to see if there's space for it
						hasSpace = getInventorySpaceEvent.parameters["hasSpaceForItem"]
						if hasSpace == inverted:
							return False, i # there wasn't space and you wanted it or vice versa, sorry.
						else:
							# there was or wasn't space for it correctly! good job!
							continue
					else:
						# no space for it
						if inverted:
							continue
						else:
							return False, i
				elif requirementType == "isUnique":
					# compares the other items in objects by reference to ensure that this object is not duplicated
					for j in range(self.numGameobjectsNeeded):
						if j != i:
							if gameobjects[j] == testsubject:
								# then it's not unique:
								if inverted:
									continue
								else:
									return False, i
					# it is unique, now figure out if that was what you wanted:
					if inverted:
						return False, i
					else:
						continue
				elif requirementType == "isDifferentFrom":
					# compares a single item, not like the isUnique which compares all of the other gameobjects.
					# also this one can use the relative or direct gameobject, so it has more options that way I guess...
					otherObject = self.getRequirementReferencedGameobject(requirement, "Item", gameobjects)
					if testsubject == otherObject:
						# it's the same
						if inverted:
							continue
						else:
							return False, i
					else:
						# it's different
						if inverted:
							return False, i
						else:
							continue
				elif distance:
					# compares the distance between two objects, Perhaps the distance between this item and another one rather than two objects?
					# why would I need two objects? I'm not fully sure why I would...
					otherObject = self.getRequirementReferencedGameobject(requirement, "Destination", gameobjects)
					# check the position for the other object
					getOtherDistanceEventParameters = {"hasPosition":False, "position":{0, 0, 0}}
					getOtherDistanceEvent = Event("getPosition", getDistanceEventParameters)
					otherEaten, otherChanged = otherObject.fire_event(getDistanceEvent)
					# check the position for the testsubject
					getDistanceEventParameters = {"hasPosition":False, "position":{0, 0, 0}}
					getDistanceEvent = Event("getPosition", getDistanceEventParameters)
					eaten, changed = otherObject.fire_event(getDistanceEvent)
					# if one of them doesn't have a position I guess I'm just going to say this test failed, even if it is inverted
					# distance implies both objects have a position I guess? Probably?
					if (not otherChanged or not changed) or (not getDistanceEvent.parameters["hasPosition"] or not getOtherDistanceEvent.parameters["hasPosition"]):
						return False, i
					thisPos = getDistanceEvent.parameters[""]
				#elif hasSeen:
					# checks if the object has noticed the other object passed here, using events, so it should be able to handle not having eyes
				# perhaps do something like
				#elif relationshipStatusIs()
				# which is a requirement based on relationship between two items (likely players). This can be used for helpig one another out
				else:
					print("this is here so I know where to add the next thing...")
		return True, -1 # I guess it works? Go for it.

	def getRequirementReferencedGameobject(self, requirement, itemKey, gameobjects):
		# returns the gameobject in question, and errors the entire program if it can't find one as it probably should
		# itemKey is appended to the end of relative or direct to get the correct answer, which means it should be capitalized
		if "relative" + itemKey in requirement:
			relativeIndex = requirement["relative" + itemKey]
			if 0 <= relativeIndex < len(gameobjects):
				return gameobjects[relativeIndex]
			else:
				print("ERROR: Unable to find relative" + itemKey + ". Index " + str(relativeIndex) + " is outside of range 0-" + str(len(gameobjects)))
				print("Requirement: " + str(requirement))
				sys.exit(0)
		elif "direct" + itemKey in requirement:
			# I don't think this one will actually work at all, so welp...
			return requirement["direct" + itemKey]
		else:
			print("ERROR: requirement has no relative or direct reference to item with itemKey " + itemKey + ": " + str(requirement))
			sys.exit(0)


	def calculate_results(self, gameobjects):
		# this uses the list of game objects as the game objects used and returns what would happen to those game objects I guess
		pass

	def get_num_gameobjects_needed(self):
		return self.numGameobjectsNeeded