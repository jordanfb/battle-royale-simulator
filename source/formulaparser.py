

"""
This class parses and evaluates the equations used to determine the chance of an actor doing each action.
It's probably just a singleton
"""
import operator
import event

class Parser:
	def __init__(self):
		pass

	def parse(self, string_eqn):
		"""returns a listEqn from a stringEqn, which can then be evaluated
		example:(1-(1-self[health])*self[trust][target[name]])*40	becomes:
				[[1, "-", [[1, "-", "self[health]"], "*", "self[trust][target[name]]"]], "*", 40]
				except actually it becomes:
				[[1.0, <built-in function sub>, [[1.0, <built-in function sub>, 'self[health]'], <built-in function mul>, 'self[trust][target[name]]']], <built-in function mul>, 40.0]
		"""
		# remove all the bad characters
		# print(string_eqn)
		remove_chars = " ,"
		for char in remove_chars:
			string_eqn = string_eqn.replace(char, "")

		eqn = []
		levels_indentation = 0
		PEMDAS = [["^"], ["*","/"], ["+","-"]] # left to right, then it just evaluates left to right inside that
		operators = {"+": operator.__add__,
					"-": operator.__sub__,
					"*": operator.__mul__,
					"/": operator.__truediv__,
					"^": operator.__pow__}
		indent_chars = "("
		deindent_chars = ")"
		i = 0
		current_section = ""
		while len(string_eqn) > i:
			# parse it more!
			if string_eqn[i] in deindent_chars:
				print("ERROR: found deindent character in stringeqn:", string_eqn)
			elif string_eqn[i] in indent_chars:
				# then recursively find out what that section is
				found = False
				layers_further_in = 0
				for other_end in range(i+1, len(string_eqn)):
					# find the other end of the indentation
					if string_eqn[other_end] in deindent_chars and layers_further_in == 0:
						# then if the length of the indented area > 0 then recursively call
						if other_end - i > 0:
							# then add the result to the list equation
							eqn.append(self.parse(string_eqn[i+1:other_end]))
							found = True
							i = other_end # skip over the section we've already recursively done
							break
					elif string_eqn[other_end] in deindent_chars:
						layers_further_in -= 1
					if string_eqn[other_end] in indent_chars:
						layers_further_in += 1
				if not found:
					print("Error finding subsection of string equation:", string_eqn)
			elif string_eqn[i] in operators:
				if len(current_section) > 0:
					eqn.append(self.try_parse_float(current_section))
					current_section = ""
				eqn.append(string_eqn[i])
			else:
				current_section += string_eqn[i]
			i += 1
		if len(current_section) > 0:
			eqn.append(self.try_parse_float(current_section))
		# then loop through your eqn and ensure order of operations is correct by "indenting" multiplications into lists
		for current_operations in PEMDAS:
			i = 0
			while i < len(eqn):
				if eqn[i] in current_operations and len(eqn) > 3:
					# len(eqn) > 3 because otherwise there's no point indenting it further, it's already by itself
					# then indent it and the things to the left and right of it
					left_part = eqn[:i-1]
					right_part = eqn[i+2:]
					# mid_part = [eqn[i-1], eqn[i], eqn[i+1]]
					mid_part = [eqn[i-1], operators[eqn[i]], eqn[i+1]]
					eqn = left_part + [mid_part] + right_part
				elif eqn[i] in current_operations:
					# then replace the operation with the math operation
					eqn[i] = operators[eqn[i]]
				else:
					i += 1
		assert(len(eqn) == 3)
		return eqn

	def try_parse_float(self, string):
		try:
			return float(string)
		except:
			return string

	def evaluate(self, list_eqn, variables):
		"""pass in the equation list made from the parse function along with the world variables in context
		string variables are going to be things like self[health]. the variables parameter is a dictionary of things like:
		{"self": selfgameobject, "target":gameobject, "weapon":gameobject}
		it looks up the variables before the square brackets, and parses them using the variables dictionary. The things inside the brackets are used as part of 
		a get event to the gameobject, where the result value of that event is what we use, so self[getHealth] will send an event with id "getHealth"
		"""
		i = 0
		# the values can only be: list, operator, or float/int constants, and the equation is asserted to be 3 long, with the middle a function I guess
		if type(list_eqn) == type(1.0):
			return list_eqn
		elif type(list_eqn) == type(""):
			return self.evaluate_string_value(list_eqn, variables)
		# otherwise, evaluate the left and right and do the operator to both of them
		# the list_eqn is a list:
		left_value = list_eqn[0]
		operator = list_eqn[1]
		right_value = list_eqn[2]
		return operator(self.evaluate(left_value, variables), self.evaluate(right_value, variables))

	def evaluate_string_value(self, string_value, variables):
		"""here we evaluate the string variables list self[getHealth] or self[getTrust, target]"""
		# this is another recursive equation solver, just with square brackets this time :P
		current_section = ""
		i = 0
		while i < len(string_value):
			if string_value[i] == "[":
				# then recursively call this function
				found = False
				subsection = ""
				layers_further_in = 0
				for closing_bracket in range(i+1, len(string_value)):
					if string_value[closing_bracket] == "]" and layers_further_in == 0:
						if closing_bracket - i > 0:
							found = True
							subsection = self.evaluate_string_value(string_value[i+1:closing_bracket], variables)
							i = closing_bracket
					elif string_value[closing_bracket] == "]":
						layers_further_in -= 1
					elif string_value[closing_bracket] == "[":
						layers_further_in += 1
				# then evaluate the current_section with the right we got here using an event
				if current_section in variables and len(subsection) > 0:
					gameobject = variables[current_section]
					e = Event(subsection, {"value":0})
					eaten, changed = gameobject.fire_event(e)
					current_section = e["value"]
				else:
					print("ERROR evaluating string value:", string_value)
			else:
				current_section += string_value[i]
			i += 1
		return current_section
