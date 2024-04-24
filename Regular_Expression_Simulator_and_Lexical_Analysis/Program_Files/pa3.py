# Name: pa3.py
# Author(s): Ben Stephen & Christine Turpen
# Date: 22 October 2020
"""
Description:
Program that defines a class named RegEx. The constructor for this class takes as its 
parameter the name of a file, and it opens and reads an alphabet and a regular expression 
from the file. The constructor then converts the regular expression to an NFA, and then
converts the NFA to a DFA. The class also has a method called simulate that takes as its 
parameter a string, and determines if the string is in the language of the regular expression.
"""

class InvalidExpression(Exception):
	pass

class Node:
	def __init__(self, symbol, left, right):
		self.symbol = symbol
		self.left = left
		self.right = right

class NFA:
	def __init__(self, states, transitions, accepts, start, alphabet):
		self.states = states
		self.transitions = transitions
		self.accepts = accepts
		self.start = start
		self.alphabet = alphabet

class DFA_State:
	def __init__(self, states, transitions):
		self.states = states
		self.transitions = transitions

class RegEx:
	def __init__(self, filename):
		"""
		Initializes a RegEx object from the specifications
		in the file whose name is filename.
		"""
		f = open(filename, 'r')
		self.alphabet = list(f.readline().strip("\n").replace(" ",""))
		regular_expression = list(f.readline().strip("\n").replace(" ",""))
		self.regular_expression = get_concat(regular_expression)
		if passes(self.regular_expression) is False:
			raise InvalidExpression

	def simulate(self, str):
		"""
		Returns True if the string str is in the language of
		the "self" regular expression.
		"""
		parse_tree = generate_parse_tree(self.regular_expression)
		my_NFA = generate_nfa(parse_tree, self.alphabet)
		DFA = {}
		DFA = generate_dfa_state(my_NFA, DFA, 0)
		need_to_update = []
		for state in DFA:
			if state != -1:
				if DFA[state].transitions == -1:
					need_to_update.append(state)
		
		while len(need_to_update) != 0:
			for state in need_to_update:
				DFA = generate_dfa_state(my_NFA, DFA, state)
				
			need_to_update = []
			for state_index in DFA:
				is_neg_1 = 0
				if len(DFA[state_index].states) == 1:
					for state in DFA[state_index].states:
						if state == -1:
							is_neg_1 = 1

				if is_neg_1 != 1:
					if DFA[state_index].transitions == -1:
						need_to_update.append(state_index)
		
		if execute_string(DFA, str, my_NFA.accepts) is True:
			return True
		else:
			return False

def get_concat(regular_expression):
	"""
	Function that takes in the regular expression and makes the implied 
	concats explicit, returning the updatted regular expression.
	"""
	dont_check = ['|', '(', 'concat']
	not_in_front = ['|', '*', 'concat', ')']
	i = 0
	length = len(regular_expression)
	while i < length:
		is_op = 0
		for op in dont_check:
			if regular_expression[i] is op:
				is_op = 1
		
		if is_op == 0:
			is_next_op = 0
			for op in not_in_front:
				try:
					if regular_expression[i + 1] is op:
						is_next_op = 1

				except:
					is_next_op = 1
			
			if is_next_op == 0:
				regular_expression.insert(i + 1, 'concat')
				length = length + 1
		i = i + 1
	
	return regular_expression

def parentheses_are_balanced(regular_expression):
	"""
	Function that takes in the regular expression and returns True or False 
	depending on whether or not the regular expression has balanced parentheses.
	"""
	left = []
	for letter in regular_expression:
		if letter == '(':
			left.append(letter)
		
		elif letter == ')':
			if len(left) > 0:
				left.pop()

			else:
				return False
	
	if len(left) > 0:
		return False

	return True

def passes(regular_expression):
	"""
	Function that takes in the regular expression and returns True or 
	False depending on whether or not the regular expression passes.
	"""
	if parentheses_are_balanced(regular_expression) is False:
		return False

def left_parenthesis(symbol, operators):
	"""
	Function that defines the parse tree behaivor when a left parenthese is encountered.
	It takes in the symbol and operators and returns the updated operators.
	"""
	operators.append(symbol)		
	return operators

def stack_empty_or_left_parentheis(operators):
	"""
	Function that takes in the operators and returns True or False depending 
	on if the stack is empty or the top of the stack contains a left parenthese.
	"""
	if len(operators) == 0:
		return False
	
	if operators[len(operators) - 1] == '(':
		return False
	
	return True
	
def right_parentheis(symbol, operators, operands):
	"""
	Function that defines the parse tree behaivor when a right parenthese is encountered.
	It takes in the symbol and operators and operands returns the updated operators and operands.
	"""
	while stack_empty_or_left_parentheis(operators) is True :
		popped = operators.pop()
		if popped == '*':
			operand_pop = operands.pop()
			tmp = Node(popped, -1, operand_pop)
			operands.append(tmp)
		
		else:
			right_pop = operands.pop()
			left_pop = operands.pop()
			tmp = Node(popped, left_pop, right_pop)
			operands.append(tmp)
	
	if len(operators) > 0:
		operators.pop()
	
	return operands, operators
	
def greater_or_equal(symbol, top_of_stack):
	"""
	Function that takes in the symbol and the top of the stack and returns True 
	or False depending on whether or not the top of stack has >= precedence.
	"""
	p = {}
	p['*'] = 3
	p['concat'] = 2
	p['|'] = 1
	p['('] = 0
	if p[top_of_stack] >= p[symbol]:
		return True
	
	return False

def not_empty_and_precedence(symbol, operator):
	"""
	Function that takes in the symbol and operator and returns True 
	or False depending on whether or not the stack is empty and if
	the the top of the stack has for an operator of >= precedence.
	"""
	if len(operator) == 0:
		return False
	
	if greater_or_equal(symbol, operator[len(operator) - 1]) is False:
		return False
	
	return True

def operator(symbol, operators, operands):
	"""
	Function that defines the parse tree behaivor when an operator is encountered.
	It takes in the symbol and operators and operands returns the updated operators and operands.
	"""
	if not_empty_and_precedence(symbol, operators):
		popped = operators.pop()
		right_pop = operands.pop()
		if popped == '*':
			tmp = Node(popped, -1, right_pop)
		
		else:
			left_pop = operands.pop()
			tmp = Node(popped, left_pop, right_pop)
		
		operands.append(tmp)
		operators.append(symbol)
	
	else:
		operators.append(symbol)

	return operators, operands

def operand(symbol, operands):
	"""
	Function that defines the parse tree when am operand is encountered.
	It takes in the symbol and operands and returns the updated operands.
	"""
	n = Node(symbol, -1, -1)
	operands.append(n)
	return operands

def empty_operator(operators, operands):
	"""
	Function that takes in the operators and operands and returns empties 
	the operator stack, returning the updated operators and operands.
	"""
	while len(operators) > 0:
		popped_op = operators.pop()
		right_pop = operands.pop()
		if popped_op == '*':
			tmp = Node(popped_op, -1, right_pop)
		
		else:
			left_pop = operands.pop()
			tmp = Node(popped_op, left_pop, right_pop)
		
		operands.append(tmp)
	
	return operators, operands

def generate_parse_tree(regular_expression):
	"""
	Function that takes in the regular expression 
	and constructs a parse tree from it.
	"""		
	operators = []
	operands = []
	for symbol in regular_expression:
		try:
			if symbol == '(':
				operators = left_parenthesis(symbol, operators)
			
			elif symbol == ')':
				operands, operators = right_parentheis(symbol, operators, operands)
			
			elif symbol == 'concat':
				operators, operands = operator(symbol, operators, operands)
		
			elif symbol == '|':
				operators, operands = operator(symbol, operators, operands)
			
			elif symbol == '*':
				operators, operands = operator(symbol, operators, operands)
			
			else:
				operands = operand(symbol, operands)

		except:
			raise InvalidExpression
	
	try:
		operators, operands = empty_operator(operators, operands)

	except:
		raise InvalidExpression

	q = []
	for x in operands:
		q.append(x)
	
	return operands[0]

def in_alphabet(symbol, alphabet):
	"""
	Function that takes in the symbol and the alphabet and returns 
	True or False depending on whether or not symbol is in the alphabet.
	"""
	for al in alphabet:
		if symbol is al:
			return True
	
	return False

def generate_nfa_leaf(symbol, alphabet):
	"""
	Function that constructs and returns an NFA 
	leaf by taking in the symbol and the alphabet.
	"""
	states = [1, 2]
	accepts = [2]
	start_state = [1]
	transitions = {}
	i = 1
	while i < len(states) + 1:
		transitions[i] = {}
		i = i + 1
	
	i = 1
	while i < len(states) + 1:
		for letter in alphabet:
			transitions[i][letter] = []
			transitions[i][letter].append(-1)
		
		transitions[i]['e'] = []
		transitions[i]['e'].append(-1)
		i = i + 1
	
	transitions[1][symbol] = []
	transitions[1][symbol].append(2)
	
	return NFA(states, transitions, accepts, start_state, alphabet)

def generate_nfa_epsilon(symbol, alphabet):
	"""
	Function that constructs and returns an NFA 
	for e by taking in the symbol and the alphabet.
	"""
	states = [1]
	start = [1]
	accepts = [1]
	transitions = {}
	for state in states:
		transitions[state] = {}
		for letter in alphabet:
			transitions[state][letter] = [-1]
		transitions[state]['e'] = [1]
	
	return NFA(states, transitions, accepts, start, alphabet)

def generate_nfa_empty_set(symbol, alphabet):
	"""
	Function that constructs and returns an NFA 
	for N by taking in the symbol and the alphabet.
	"""
	states = [1]
	start = [1]
	accepts = []
	transitions = {}
	for state in states:
		transitions[state] = {}
		for letter in alphabet:
			transitions[state][letter] = [-1]
		transitions[state]['e'] = [-1]
	
	return NFA(states, transitions, accepts, start, alphabet)

def star_nfa(nfa_a):
	"""
	Function that takes in an NFA, stars 
	it, and returns the starred NFA.
	"""
	new_start = [1]
	new_states = [1]
	for state in nfa_a.states:
		new_states.append(state + 1)
	
	new_accepts = [1]
	for accept_a in nfa_a.accepts:
		new_accepts.append(accept_a + 1)
	
	new_transitions = {}
	for state in new_states:
		new_transitions[state] = {}
	
	for symbol in nfa_a.transitions[1]:
		new_transitions[1][symbol] = []
		if symbol == 'e':
			for start_a in nfa_a.start:
				new_transitions[1][symbol].append(start_a + 1)
		
		else:
			new_transitions[1][symbol].append(-1)
	
	for state_a in nfa_a.transitions:
		new_state = state_a + 1
		for symbol in nfa_a.transitions[1]:
			new_transitions[new_state][symbol] = []
			for trans_state in nfa_a.transitions[state_a][symbol]:
				if trans_state != -1:
					new_transitions[new_state][symbol].append(trans_state + 1)
				
				else:
					new_transitions[new_state][symbol].append(-1)
	
	for accept_a in nfa_a.accepts:
		new_transitions[accept_a + 1]['e'] = []
		for start_a in nfa_a.start:
			new_transitions[accept_a + 1]['e'].append(start_a + 1)
	
	return NFA(new_states, new_transitions, new_accepts, new_start, nfa_a.alphabet)

def union_nfas(nfa_a, nfa_b):
	"""
	Function that takes in two NFAs, unions 
	them, and returns the unioned NFA.
	"""
	states = []
	for x in range(1, len(nfa_b.states) + len(nfa_a.states) + 2):
		states.append(x)

	new_accepts = []
	for a_accepts in nfa_a.accepts:
		new_accepts.append(a_accepts + 1)
	
	for b_accepts in nfa_b.accepts:
		new_accepts.append(b_accepts + len(nfa_a.states) + 1)
	
	new_start = [1]
	new_transitions = {}
	new_transitions[1] = {}
	for symbol in nfa_a.transitions[1]:
		if symbol != 'e':
			new_transitions[1][symbol] = []
			new_transitions[1][symbol].append(-1)
		
		else:
			new_transitions[1][symbol] = []
			for a_start in nfa_a.start:
				new_transitions[1][symbol].append(a_start + 1)
			
			for b_start in nfa_b.start:
				new_transitions[1][symbol].append(b_start + len(nfa_a.states) + 1)

	state_num = 2
	while state_num <= len(nfa_b.states) + len(nfa_a.states) + 1:
		new_transitions[state_num] = {}
		if state_num <= len(nfa_a.states) + 1:
			for symbol in nfa_a.transitions[state_num - 1]:
				new_transitions[state_num][symbol] = []
				for trans_state in nfa_a.transitions[state_num - 1][symbol]:
					if trans_state != -1:
						new_transitions[state_num][symbol].append(trans_state + 1)
					
					else:
						new_transitions[state_num][symbol].append(-1)
		
		else:
			for symbol in nfa_b.transitions[state_num - len(nfa_a.states) - 1]:
				new_transitions[state_num][symbol] = []
				for trans_state in nfa_b.transitions[state_num - len(nfa_a.states) - 1][symbol]:
					if trans_state != -1:
						new_transitions[state_num][symbol].append(trans_state + len(nfa_a.states) + 1)
					else:
						new_transitions[state_num][symbol].append(-1)
		
		state_num = state_num + 1
		
	return NFA(states, new_transitions, new_accepts, new_start, nfa_a.alphabet)

def concat_nfas(nfa_a, nfa_b):
	"""
	Function that takes in two NFAs, concats 
	them, and returns the concated NFA.
	"""
	new_states = []
	for x in range(1, len(nfa_b.states) + len(nfa_a.states) + 1):
		new_states.append(x)
	
	new_accepts = []
	for accept_b in nfa_b.accepts:
		new_accepts.append(accept_b + len(nfa_a.states))
	
	new_starts = []
	for start_a in nfa_a.start:
		new_starts.append(start_a)
	
	new_transitions = {}
	for state_index in new_states:
		new_transitions[state_index] = {}
		for symbol in nfa_a.transitions[1]:
			new_transitions[state_index][symbol] = []
			if state_index <= len(nfa_a.states):
				for trans_state in nfa_a.transitions[state_index][symbol]:
					if trans_state != -1:
						new_transitions[state_index][symbol].append(trans_state)

					else:
						new_transitions[state_index][symbol].append(-1)
				
				if symbol == 'e':
					for accept_a in nfa_a.accepts:
						if state_index is accept_a:
							for start_b in nfa_b.start:
								new_transitions[state_index][symbol].append(start_b + len(nfa_a.states))
			
			else:
				for trans_state in nfa_b.transitions[state_index - len(nfa_a.states)][symbol]:
					if trans_state != -1:
						new_transitions[state_index][symbol].append(trans_state + len(nfa_a.states))
						
					else:
						new_transitions[state_index][symbol].append(-1)
	
	return NFA(new_states, new_transitions, new_accepts, new_starts, nfa_a.alphabet)

def generate_nfa(parse_tree, alphabet):
	"""
	Function that makes and returns the NFA by 
	taking in the parse tree and the alphabet.
	"""
	tree = parse_tree
	curr_nfa = -1 
	if in_alphabet(tree.symbol, alphabet):
		curr_nfa = generate_nfa_leaf(tree.symbol, alphabet)
	
	elif tree.symbol == 'e':
		curr_nfa = generate_nfa_epsilon(tree.symbol, alphabet)
	
	elif tree.symbol == 'N':
		curr_nfa = generate_nfa_empty_set(tree.symbol, alphabet)
	
	elif tree.symbol == '*':
		curr_nfa = star_nfa(generate_nfa(tree.right, alphabet))
	
	elif tree.symbol == '|':
		curr_nfa = union_nfas(generate_nfa(tree.left, alphabet), generate_nfa(tree.right, alphabet))
	
	elif tree.symbol == 'concat':
		curr_nfa = concat_nfas(generate_nfa(tree.left, alphabet), generate_nfa(tree.right, alphabet))
	
	return curr_nfa

def get_epsilons(state, transitions, epsilons):
	"""
	Function that takes in a state, a list of transitions and 
	epsilons and returns all the pssobile epsilon transitions.
	"""
	if state == -1:
		return epsilons
	
	for trans_state in transitions[int(state)]['e']:
		if trans_state != -1:
			epsilons.append(trans_state)
			try:
				epsilons = get_epsilons(trans_state, transitions, epsilons)

			except:
				pass
	
	return epsilons

def remove_duplicates(possible_states):
	"""
	Takes in a list of possible NFA states and removes 
	duplicates. from the list of possible NFA states.
	"""
	t = []
	for x in possible_states:
		if x not in t:
			t.append(x)

	return t

def remove_negative_1(transitions):
	"""
	Function that takes in a list of transitions 
	and removes -1 and returns the updates list.
	"""
	for state in transitions:
		if len(transitions) > 1:
			if state == -1:
				transitions.remove(state)
	
	return transitions

def state_exists(list, DFA):
	"""
	Function that takes in a DFA and a list of DFA states and 
	returns if the DFA state has already been created
	"""
	for dfa_index in DFA:
		if len(list) is len(DFA[dfa_index].states):
			counterpart = 0
			for state in DFA[dfa_index].states:
				for member_of_my_list in list:
					if member_of_my_list is state:
						counterpart = counterpart + 1
			
			if counterpart is len(list):
				return dfa_index
	
	return -1

def state_self(list, self):
	"""
	Function that takes in a list of transitions and their 
	possible statesand checks if the state has a self transition.
	"""
	if len(list) is len(self):
		counterpart = 0
		for x in list:
			for y in self:
				if x is y:
					counterpart = counterpart + 1
		
		if counterpart is len(self):
			return True
	
	return False

def generate_dfa_state(nfa, DFA, id_for_new_state):
	"""
	Function that takes in thr NFA, the DFA, the ID 
	for the new state and returns the DFA state.
	"""
	curr_states = []
	if len(DFA) == 0:
		for start_state in nfa.start:
			curr_states.append(start_state)
	
	else:
		curr_states = DFA[id_for_new_state].states
	
	possible_states = []
	new_transitions = {}
	for single_state in curr_states:
		possible_states.append(single_state)
		possible_states = get_epsilons(single_state, nfa.transitions, possible_states)
		possible_states = remove_duplicates(possible_states)
	
		for symbol in nfa.alphabet:
			new_transitions[symbol] = []
		
		for one_possible in possible_states:
			for symbol in nfa.alphabet:
				try:
					for tran_state in nfa.transitions[int(one_possible)][symbol]:
						new_transitions[symbol].append(tran_state)
						new_transitions[symbol] = get_epsilons(tran_state, nfa.transitions, new_transitions[symbol])

				except:
					new_transitions[symbol].append(-1)
				
				new_transitions[symbol] = remove_negative_1(new_transitions[symbol])
				new_transitions[symbol] = remove_duplicates(new_transitions[symbol])
		
		trans = {}
		trans_id = len(DFA) + 1
		for symbol in nfa.alphabet:
			trans[symbol] = -1
			a = state_exists(new_transitions[symbol], DFA)
			b = state_self(new_transitions[symbol], possible_states)
			if b is True:
				trans[symbol] = id_for_new_state
			
			elif a == -1:
				trans[symbol] = trans_id
				DFA[trans_id] = DFA_State(new_transitions[symbol], -1)
				trans_id = trans_id + 1
            
			else:
				trans[symbol] = a
				
		DFA[id_for_new_state] = DFA_State(possible_states, trans)
	
	return DFA

def execute_string(DFA, string, accepts):
	"""
	A function that takes in the DFA dictionary, the input string, 
	and the accept states and runs the string on a DFA.
	"""
	string = list(string)
	curr = 0
	for letter in string:
		for x in DFA[DFA[curr].transitions[letter]].states:
			if x == -1:
				return False
		curr = DFA[curr].transitions[letter]
		
	a = 0
	for nfastate in DFA[curr].states:
		if nfastate in accepts:
			a = 1
			return True
	
	if a == 0:
		return False