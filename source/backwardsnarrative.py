"""
This is trying to simulate the hunger games but backwards, so we start with the winner and figure out who
they killed (or if the other person just died) and so on and so forth until we arrive at the beginning.
This is in an attempt to make a narratively coherent hunger games simulation which allows for designing the
intensity of the action and so on moreso than a purely agent based simulation allows for.

What's the length of a simulation step? Something like a quarter day? That makes some sense. That's a whole
lot of events to write though... that's alright I can rope Schuyler into it. That allows for some granularity
but not too much granularity.


Almost want a backwards pass to set up the plot and then a forwards pass to justify it and add references to
things that happened in the past like twisting your ankle or some injury or previous encounter...
"""

import random


class Character:
	def __init__(self, name, stats):
		self.name = name
		self.stats = stats # a dictionary of string to floats probably.
		self.death_backwards_index = 0

	def __repl__(self):
		return self.name

	def __str__(self):
		return self.__repl__()


class Event:
	def __init__(self):
		pass

class KillEvent (Event):
	# kill events are only kill events when experienced forwards in time,
	# so they actually create characters in the simulation
	# These are one of the two primary types of events

	def __init__(self):
		pass

	def unkill_character(self, simulation, characters):
		# add the characters back to the simulation!
		for c in characters:
			simulation.dead.remove(c)
			# if c not in simulation.available_alive_characters:
			# 	simulation.available_alive_characters += [c]
			if c not in simulation.alive:
				simulation.alive += [c]

class StabEvent(KillEvent):
	def __init__(self):
		pass

	def get_possible_occurances(self, simulation):
		possible = []
		if len(simulation.available_alive_characters) > 0 and len(simulation.dead) > 0:
			for killer in simulation.available_alive_characters:
				for victim in simulation.dead:
					possible += [lambda sim : self.run_event(sim, killer, victim)]
		return possible # can only happen if no one is alive!

	def run_event(self, simulation, killer, victim):
		KillEvent.unkill_character(self, simulation, [victim])
		simulation.available_alive_characters.remove(killer) # they did their action!
		return FinishedEvent(str(killer) + " stabs " + str(victim) + ".", [killer, victim])


# This "unkills" the winner of the hunger games. It's an extra "free" step at the end of the games
class WinEvent (KillEvent):
	def __init__(self):
		pass

	def get_possible_occurances(self, simulation):
		possible = []
		if len(simulation.alive) == 0:
			for p in simulation.dead:
				possible += [lambda sim : self.run_event(sim, p)]
		return possible # can only happen if no one is alive!

	def run_event(self, simulation, character):
		KillEvent.unkill_character(self, simulation, [character])
		return FinishedEvent(str(character) + " wins the Hunger Games!", [character])

class SimpleEvent:
	def __init__(self, text):
		self.turns_since_use = -1
		self.text = text
		self.characters = []
		for i in range(0, 100):
			if "[c" + str(i) + "]" in self.text:
				self.characters += ["[c" + str(i) + "]"] # add the string to replace!

	def get_possible_occurances(self, simulation):
		possible = []
		if len(simulation.available_alive_characters) >= len(self.characters):
			# print([[str(y) for y in x] for x in self.chose_random_character_permutation(simulation.available_alive_characters, 2)])
			# for p in simulation.available_alive_characters:
			# 	possible += [lambda sim : self.run_event(sim, [p])]
			for p in self.chose_random_character_permutation(simulation.available_alive_characters, len(self.characters)):
				# create an option for them!
				possible += [lambda sim : self.run_event(sim, p)]
		return possible # can only happen if no one is alive!

	def chose_random_character_permutation(self, characters, num):
		options = []
		if num == 1:
			# base case, return each character
			return [[x] for x in characters]
		elif num > 1:
			for i in range(len(characters)):
				chosen = characters[i]
				recursive_call = self.chose_random_character_permutation([x for x in characters if x != chosen], num-1)
				recursive_call = [x + [chosen] for x in recursive_call] # append the chosen one!
				options += recursive_call
		return options

	def run_event(self, simulation, characters):
		text = self.text
		for i in range(len(self.characters)):
			simulation.available_alive_characters.remove(characters[i])
			text = text.replace(self.characters[i], str(characters[i]))
		return FinishedEvent(text, characters)


class FinishedEvent:
	# this is used for IDK purposes?
	def __init__(self, text, characters):
		self.text = text
		self.characters = characters

	def get_text(self):
		return self.text

class EventDictionary:
	# This is what chooses what event to fire next? I think?
	# Arguably this should just be the simulation? :P
	# Need to evaluate which events can be done...
	# events should return their chance of happening I guess?
	# presumably each person can only do one action per step?
	# then just check which people are free again and go from there? It works...
	# Some events are killing events, some are just "filler" events. We have that division because
	# we want it for pacing
	pass


class Simulation:
	def __init__(self, characters):
		self.characters = characters
		self.alive = []
		self.dead = self.characters
		self.num_backwards_steps = 0
		self.steps = [] # each step is itself a list of events that occured during the step? Makes some sense
		self.winner = None
		self.possible_kill_events = [WinEvent(), StabEvent()]
		self.possible_events = [SimpleEvent("[c1] and [c2] spot each other but [c1] runs away."), SimpleEvent("[c1] looks for food.")]
		self.available_alive_characters = []

	def simulate_step(self, num_deaths):
		# this works backwards! Starting from the winner and everyone else dead 
		# and moving towards everyone being alive
		self.num_backwards_steps += 1
		new_step = []
		self.available_alive_characters = [x for x in self.alive]
		for i in range(num_deaths):
			possible = []
			for e in self.possible_kill_events:
				possible += e.get_possible_occurances(self)
			if len(possible) == 0:
				print("No events found")
				break
			else:
				to_run = random.choice(possible)
				new_step.append(to_run(self)) # returns the created post event
		while True:
			# now run random filler events
			possible = []
			for e in self.possible_events:
				possible += e.get_possible_occurances(self)
			if len(possible) == 0:
				break
			else:
				to_run = random.choice(possible)
				new_step.append(to_run(self)) # returns the created post event
		random.shuffle(new_step) # shuffle the step! yeah!
		if len(new_step) > 0:
			self.steps = [new_step] + self.steps # add the step to the front which is when it happened
		return len(new_step) > 0 # if there's more to simulate!

	def get_step_from_backwards(self, backwards_index):
		return self.steps[len(self.steps)-backwards_index-1]

	def __repl__(self):
		# I'm gonna try to make this for debugging not for story stuff
		s = "Simulation State:\nLive Characters:\n"
		for c in self.alive:
			s += "	" + str(c.__repl__()) + "\n"
		s += str(len(self.steps)) + " Steps:\n"
		for step in self.steps:
			s += "	"
			s += " ".join([e.get_text() for e in step])
			# for event in step:
			# 	s += str(event) + ", "
			s += "\n"
		return s

	def __str__(self):
		return self.__repl__()


if __name__ == "__main__":
	characters = []
	names = ["Jordan", "Jenna", "Joe", "Schuyler", "Tom", "Eli"]
	for n in names:
		characters += [Character(n, {})]

	sim = Simulation(characters)
	simulate_next_step = True
	simulate_next_step = sim.simulate_step(1) # this just adds the "wins hunger games" event
	simulate_next_step = sim.simulate_step(1) # this one is the death that causes the win
	while simulate_next_step and sim.num_backwards_steps < 500 and len(sim.dead) > 0:
		simulate_next_step = sim.simulate_step(random.choice([0,0,0,1,1,1,2]))
	print(sim)