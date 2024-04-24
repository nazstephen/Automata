# Name: pa2.py
# Author(s): Ben Stephen & Christine Turpen
# Date: 10 October 2020
"""
Description: Program that defines a class named NFA. The constructor for
this class reads an NFA specification from a file. The class also has a
method that converts the NFA to an equivalent DFA, and writes the DFA to
a file, using the same DFA file format as specified in pa1.
"""

class NFA:
	""" Simulates an NFA """

	def generate_nfa_dict(self, transition_functions):
		"""
		Generates and returns the NFA dictionary by passing 
		in the transition functions from the read in file.
		"""

		# Use the transition functions to generate a matrix of 
		# the keys that will later be added into the NFA dictionary
		rows, cols = (len(transition_functions), 2) 
		matrix = [[0 for i in range(cols)] for j in range(rows)]
		for x in range(len(transition_functions)):
			matrix[x][0] = int(transition_functions[x][0])
			matrix[x][1] = transition_functions[x][1]
		
		# Sort the keys
		for x in range(len(matrix)):
			for j in range(0, len(matrix) - x -1):
				if matrix[j][0] > matrix[j + 1][0]:
					matrix[j], matrix[j +1 ] = matrix[j + 1], matrix[j]

		# Convert the keys from the matrix into tuples
		# which will be added into the NFA dictionary
		for x in range(len(matrix)):
			matrix[x][0] = str(matrix[x][0])
		nfa_keys = tuple(tuple(i) for i in matrix)
	
		# Declare the NFA dictionary and pass in the keys 
		nfa_dict = {}
		list = []
		nfa_dict[nfa_keys[0]] = list
		x = 1
		for x in range(len(nfa_keys)):
			if nfa_keys[x] not in nfa_dict:
				nfa_dict[nfa_keys[x]] = 0
	
		# Adds values (ending states of transition functions) 
		# to their corresponding NFA keys (starting state and 
		# transition) in the NFA dictionary
		nfa_values = tuple(tuple(i) for i in transition_functions)
		for x in nfa_dict:
			nfa_dict[x] = []
			for i in range(len(nfa_values)):
				if x == nfa_values[i][0:2]:
					nfa_dict[x].append(transition_functions[i][2])
		return nfa_dict


	def __init__(self, nfa_filename):
		"""
		Initializes NFA from the file whose name is
		nfa_filename.(So you should create an internal representation
		of the nfa.) Places NFA into a dictionary
		"""

		#Opens the NFA text file
		f = open(nfa_filename, 'r')
		lines = f.readlines()
		f.close()
		
		#Initializes number of states in NFA
		self.num_states = lines[0]

		#Initializes the alphabet of the NFA
		self.alphabet = lines[1].rstrip()

		#Initializes the transition functions of the NFA
		start_transition_index = 2
		end_transition_index = len(lines) - 3
		NFA_transition_lines = lines[start_transition_index:end_transition_index]
		self.transition_functions = []
		for line in NFA_transition_lines:
			line = line.split()
			self.transition_functions += [[char.replace("'", '').replace(' ', '') for char in line]]

		#Initializes the start state of the NFA
		self.start_state = lines[-2].rstrip()

		#Initializes the accept states of the NFA
		self.accept_states = lines[-1]

		#Initializes the NFA dictionary
		self.nfa_dict = self.generate_nfa_dict(self.transition_functions)


	def epsilon_closure(self, nfa_dict, state):
		"""
		Takes in the NFA dictionary and a state to return 
		the epsilon closure of that particular state.
		"""

		nfa_value = nfa_dict.get((state, "e"))
		arr = []
		if nfa_value == None:
			arr.append(state)
			return arr
		key = (state, "e")
		tuples = nfa_dict[key].copy()
		list_of_tuples = [state]
		final_list_of_tuples = []
		while len(tuples) > 0:
			state = [tuples.pop(0)]
			list_of_tuples.append(state[0])
			if(isinstance(state[0], list)):
				for i in range(len(state[0])):
					temp_value = (state[0][i], "e")
					if nfa_dict.get(temp_value) != None:
						temp_list = nfa_dict[temp_value]
						tuples.append(temp_list)
			else:
				for j in range(len(state)):
					temp_value = (state[j], "e")
					if nfa_dict.get(temp_value) != None:
						temp_list = nfa_dict[temp_value]
						tuples.append(temp_list)
		for k in range(len(list_of_tuples)):
			if(isinstance(list_of_tuples[k], list)):
				for l in range(len(list_of_tuples[k])):
					final_list_of_tuples.append(list_of_tuples[k][l])
			else:
				final_list_of_tuples.append(list_of_tuples[k])
		return final_list_of_tuples


	def generate_dfa_dict(self, nfa_dict, alphabet, start_state):
		"""
		Takes in the NFA dictionary, the alphabet, and the start 
		state and returns the DFA dictionary.
		"""

		dfa_dict = {}
		arr = []
		arr.append(self.epsilon_closure(nfa_dict, start_state))
		curr_state = self.epsilon_closure(nfa_dict, start_state)
		start_states = list(dict.fromkeys(self.epsilon_closure(nfa_dict, start_state)))
		start_states.sort()
		tuples = tuple(tuple(i) for i in start_states)
		dictionary = {}
		dictionary[tuples] = "0"
		while(len(arr) > 0):
			curr_state = arr.pop(0)
			for j in range(len(alphabet)):
				transitions_list = []
				for k in range(len(curr_state)):
					key0 = (curr_state[k], alphabet[j])
					if key0 in nfa_dict:
						eclosure0 = self.epsilon_closure(nfa_dict, curr_state[k])
						for l in range(len(eclosure0)):
							key1 = (eclosure0[l], alphabet[j])
							if key1 in nfa_dict:
								for m in range(len(nfa_dict[key1])):
									nfa_dict[key0].append(nfa_dict[key1][m])
						nfa_dict[key0] = list(dict.fromkeys(nfa_dict[key0]))
						transitions_list.append(nfa_dict[key0])
					else:
						eclosure1 = self.epsilon_closure(nfa_dict, curr_state[k])
						for n in range(len(eclosure1)):
							key2 = (eclosure1[n], alphabet[j])
							if key2 in nfa_dict:
								for r in range(len(nfa_dict[key2])):
									transitions_list.append(nfa_dict[key2][r])
				dfa_states = []
				for o in range(len(transitions_list)):
					if(isinstance(transitions_list[o], list)):
						for p in range(len(transitions_list[o])):
							dfa_states.append(transitions_list[o][p])
					else:
						dfa_states.append(transitions_list[o])
				dfa_states = list(dict.fromkeys(dfa_states))
				dfa_states.sort()
				dfa_dict[(tuple(curr_state), alphabet[j])] = dfa_states
				tuples = tuple(tuple(q) for q in dfa_states)
				if tuples in dictionary:
					continue
				else:
					dictionary[tuples] = "0"
					arr.append(dfa_states)
		return dfa_dict


	def condense_dfa_states(self, dfa_dict, alphabet):
		"""
		Function that takes in the DFA dictionary and the alphabet and
		creates a dictionary where the DFA states (tuples) are added
		as keys, with their condensed corresponding states as values.
		Returns this dictionary.
		"""

		dfa_keys = []
		condensed_states = {}
		counter = 1
		for key in dfa_dict.keys():
			dfa_keys.append(key)
		while len(dfa_keys) > 0:
			key = dfa_keys.pop(0)
			condensed_states[key[0]] = str(int((counter / len(alphabet))))
			counter = counter + 1
		return condensed_states


	def write_dfa_transition_functions(self, dfa_dict, condensed_states, f):
		"""
		Takes in the DFA dictionary, the dictionary of the condensed DFA 
		states, and the opened DFA file as its parameters. The algorithm 
		generates the transition functions of the DFA and and writes them 
		onto the DFA file line by line.
		"""

		dfa_keys = []
		for key in dfa_dict.keys():
			dfa_keys.append(key)
		for i in range (len(dfa_keys)):
			dfa_key = dfa_keys[i][0]
			transition = dfa_keys[i][1]
			starting_state = condensed_states[dfa_key]
			dfa_value = dfa_dict[dfa_keys[i]]
			new_dfa_value = tuple(j for j in dfa_value)
			ending_state = condensed_states[new_dfa_value]
			transition_function = starting_state + " '" + transition + "' " + ending_state
			f.write(transition_function + "\n")

	def write_dfa_accept_states(self, dfa_dict, alphabet, accept_states, f):
		"""
		Takes in the DFA dictionary, the alphabet, the NFA accept states, and the 
		opened DFA file as its parameters. Finds the matching accept states in the 
		DFA dicionary and writes them to the DFA text file in a single line.
		"""
        
		dfa_keys = []
		dfa_accept_states = []
		accept_states_dict = {}
		for i in range (len(accept_states.split(' '))):
			accept_states_dict[accept_states.split(' ')[i]] = "0"
		new_state_num = 1
		for key in dfa_dict.keys():
			dfa_keys.append(key)
		num_loops = 0
		while len(dfa_keys) > 0:
			single_key = [item for j in dfa_keys.pop(0) for item in j]
			single_key.pop()
			for k in range((len(single_key))):
				if single_key[k] in accept_states_dict:
					dfa_accept_states.append(new_state_num)
			num_loops = num_loops + 1
			if num_loops == len(alphabet):
				new_state_num = new_state_num + 1
				num_loops = 0
		for l in range(len(list(dict.fromkeys(dfa_accept_states)))):
			f.write(str(list(dict.fromkeys(dfa_accept_states))[l])+ " ")


	def toDFA(self, dfa_filename):
		"""
		Converts the "self" NFA into an equivalent DFA
		and writes it to the file whose name is dfa_filename.
		The format of the DFA file must have the same format
		as described in the first programming assignment (pa1).
		This file must be able to be opened and simulated by your
		pa1 program.

		This function should not read in the NFA file again.  It should
		create the DFA from the internal representation of the NFA that you 
		created in __init__.
		"""
		
		# Generate DFA dictionary
		self.dfa_dict = self.generate_dfa_dict(self.nfa_dict, self.alphabet, self.start_state)

		#Generate dictionary of condensed DFA states  
		self.condensed_states = self.condense_dfa_states(self.dfa_dict, self.alphabet)

		#Opens a DFA text file
		f = open(dfa_filename, 'a')
		
		#Writes the number of states to the DFA text file
		f.write(str(len(self.condensed_states.keys())) + "\n")

		#Writes the alphabet to the DFA text file
		f.write(str(self.alphabet) + "\n")

		#Writes the transition functions to the DFA text file
		self.write_dfa_transition_functions(self.dfa_dict, self.condensed_states, f)
		
		# Writes the start state to the DFA text file
		# The start state will always be 1 for every DFA
		f.write("1" + "\n")

		# Writes the accept states to the DFA text file
		self.write_dfa_accept_states(self.dfa_dict, self.alphabet, self.accept_states, f)