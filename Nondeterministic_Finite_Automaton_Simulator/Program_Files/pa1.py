# Name: pa1.py
# Author(s): Ben Stephen and Christine Turpen
# Date: September 10, 2020
""" 
Description: We were tasked to define a class called DFA, 
which contains a constructor that takes the name of a file 
as its parameter, and initializes the DFA from its contents. 
The DFA should also contain a method that takes a string as 
its parameter, and returns True if the string is in the 
language of the DFA, and false if not.
"""
import sys

class DFA:
	""" Simulates a DFA """

	def __init__(self, filename):
		"""
		Initializes DFA from the file whose name is
		filename
		"""

		#Initialize number of states and alphabet
		count0 = 0
		with open(filename, 'r') as f:
			for line in f:
				if count0 == 0:
					self.num_states = int(line)
					count0 += 1
				if count0 == 2:
					self.alphabet = line
					count0 +=1
				count0 += 1
		f.close()

		#Initialize dictionary with transition functions. Also initialize start state and accept states 
		tf = {}
		cap = self.num_states * (len(self.alphabet) - 1) #Cap tells us how many lines in the file are transitions
		count1 = 0
		with open(filename) as f:
			for line in f:
				if(count1 > 1 and count1 < (cap + 2)):
					#Create a key with the start state and transition. Make destination the output
					(start, transition, dest) = line.split()
					s = int(start)
					t = transition.replace("'","")
					d = int(dest)
					tf[s, t] = d
				if(count1 == (cap + 2)):
					self.start_state = int(line) #Initialize start state
				if(count1 == (cap + 3)):
					#Split string to list of integers
					a_list = line.split()
					map_object = map(int, a_list)
					self.accept_states = list(map_object) #Initialize accept states
				count1 += 1
		f.close()

		#Initialize transition functions
		self.transition_function = tf
	
	def transition(self, input_value):
		"""
		Handles transitions in simulation based on input str
		"""

		self.curr = self.transition_function[(self.curr, input_value)]
		return

	def in_dfa_lang(self):
		"""
		Returns true if the string is in the language of the DFA
		"""

		return self.curr in self.accept_states
    
	def go_to_start(self):
		"""
		Returns the initial state of DFA
		"""

		self.curr = self.start_state
		return

	def simulate(self, str):
		""" 
		Simulates the DFA on input str.  Returns
		True if str is in the language of the DFA,
		and False if not.
		"""
		
		self.go_to_start()
		for input_value in str:
			self.transition(input_value)
			continue
		return self.in_dfa_lang()