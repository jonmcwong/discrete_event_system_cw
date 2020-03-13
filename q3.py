import numpy as np

# helper functions

# print every item in a list
def printList(l):
	for x in l:
		print(x)

# A class for a generic automaton

class G:
	def __init__(self,E,X,T,x0):
		self.E = E 			# list of events
		self.X = X 			# list of states
		self.T = T 			# list of transitions, each transition is a tuple (x,x',e)
		self.x0 = x0 		# initial state

	def transition(self, x, e):

		# Look for all transitions that start at x and e happens
		possible_transtions = [transition for transition in self.T if transition[0]==x and transition[2]==e]

		# if the event and state pair is not defined
		if len(possible_transtions) == 0:
			return None

		# Non-deterministic case
		elif len(possible_transtions) > 1:
			# print([transition[1] for transition in possible_transitions])
			return [transition[1] for transition in possible_transitions]

		else:

			# Return the destination state
			return [possible_transtions[0][1]]

	# function that takes an automaton, a list of events of partially observable

	def makeEventsPartiallyObservable(self, E_partialObs, e_replace):

		# iterate through events and their indices in the event list
		found_flag = False
		for idx, e in enumerate(self.E):
			if e in E_partialObs:
				self.E[idx] = e_replace

		new_E = []
		for e in self.E:
			if e not in new_E:
				new_E.append(e)
		self.E = new_E


		for idx, transition in enumerate(self.T):
			if transition[2] in E_partialObs:
				self.T[idx] = (transition[0], transition[1], e_replace)

	def isEnabled(self, x, e):
		possible_transitions = [transition for transition in self.T if transition[0]==x and transition[2]==e]
		if len(possible_transitions)>0:
			return True
		else:
			return False

	def printG(self):
		print("List of ", len(self.E), " events E")
		printList(self.E)
		print("Initial state:")
		print(self.x0)
		print("List of ",len(self.X), " states X")
		printList(self.X)
		print("List of ", len(self.T), " enabled transitions T")
		printList(self.T)

	def traverseG(self, word, x0):
		curr_x = x0
		
		# iteratively apply each event in the word
		for e in word:

			# return undefined if the previous transition was undefined
			if self.transition(curr_x, e) == None:
				return None

			# choose the first one for now
			# transition returns a list in the general case
			curr_x = self.transition(curr_x, e)[0]


		return curr_x

	def getXRowSum(self):
		X = np.asarray(self.X)
		rowSum = np.sum(X, axis=1)
		return rowSum

	def getXColSum(self):
		X = np.asarray(self.X)
		colSum = np.sum(X, axis=0)
		return colSum

	def getXSingVals(self):
		X = np.asarray(self.X)
		s = np.linalg.svd(X, compute_uv=False)
		# print(s)
		return s.tolist()

def getParallelComposition(G1,G2):

	# states
	x_new = [] # list of states to explore
	x_old = [] # list of explored states

	# events
	E_temp = G1.E + G2.E 	# concatenation
	E_parallel = []
	for e in E_temp:
		if e not in E_parallel:
			E_parallel.append(e) 

	# transitions
	T_parallel = []

	# Add an initial state to search
	x_new.append((G1.x0, G2.x0))

	# for every unsearched state
	while len(x_new) > 0:
		x1,x2 = x_new[0]
		for e in E_parallel:
			next_x1,next_x2 = G1.transition(x1,e), G2.transition(x2,e)

			# if event is exists in both automata
			if e in G1.E and e in G2.E:
				
				# if event is enabled in both automata
				if G1.isEnabled(x1,e) and G2.isEnabled(x2,e):   # useless
					all_possible_x = [(x,y) for x in next_x1 for y in next_x2]
					for next_x in all_possible_x:
						T_parallel.append((x_new[0], next_x, e))

						# update x_new if new state
						if next_x not in x_old and next_x not in x_new:
							x_new.append(next_x)

			# if event is private to G1
			elif e in G1.E:
				if G1.isEnabled(x1,e):
					all_possible_x = [(x,y) for x in next_x1 for y in [x2]]
					for next_x in all_possible_x:
						T_parallel.append((x_new[0], next_x, e))

						# update x_new if new state
						if next_x not in x_old and next_x not in x_new:
							x_new.append(next_x)
			# if event is private to G2
			elif e in G2.E:
				if  G2.isEnabled(x2,e):
					all_possible_x = [(x,y) for x in [x1] for y in next_x2]
					for next_x in all_possible_x:
						T_parallel.append((x_new[0], next_x, e))

						# update x_new if new state
						if next_x not in x_old and next_x not in x_new:
							x_new.append(next_x)

			# e doesn't exist in either automata
			else:
				print("something bad happended")


		
		x_old.append(x_new[0])
		del x_new[0]
	return G(E_parallel,x_old,T_parallel,(G1.x0,G2.x0))

def getObserverG(G_in,x0):

	# initialise empty variables
	x_new = []		# list of states to explore
	x_old = []		# list of explored states
	T_obs = []		# list of transitions
	x_new.append(x0)

	# explore every state in x_new
	while len(x_new) > 0:

		# for a given state x to explore, try every possible event
		for e in G_in.E:
			possible_dest = []

			# get list of possible next states of the partially observed automaton in Q4
			for idx, x in enumerate(G_in.X):
				if x_new[0][idx] == 1:
				# add all possible destination states
					if G_in.transition(x,e) != None:
						possible_dest.extend(G_in.transition(x,e))

			# build next state from 1s and 0s for observer automaton
			next_x = []
			for x in G_in.X:
				if x in possible_dest:
					next_x.append(1)
				else:
					next_x.append(0)

			# if there was at least one event that was defined, add to list of transitions
			if len(possible_dest) > 0:
				T_obs.append((x_new[0],next_x,e))

				# update x_new if new state
				if next_x not in x_old and next_x not in x_new:
					x_new.append(next_x)

		# update explored states
		x_old.append(x_new[0])
		del x_new[0]

	return G(G_in.E, x_old, T_obs, x0)


# q3
print("\n\n\nQ3")
# Test parallel composition for robot and map

E_Gr = ['r','n','e','s','w']	# set of events for Gr
X_Gr = ['n','e','s','w']		# set of states in Gr
T_Gr = [('n','e','r'),			# set of enabled transitions for Gr
				('e','s','r'),
				('s','w','r'),
				('w','n','r'),
				('n','n','n'),
				('e','e','e'),
				('s','s','s'),
				('w','w','w')]
x0_Gr = 'n'						# initial state for Gr
Gr = G(E_Gr, X_Gr, T_Gr, x0_Gr)	# Declare Gr as an automaton

E_Gm = ['n','e','s','w']		# set of events for Gm
X_Gm = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7']	# set of states in Gm
T_Gm = [('r1','r2','e'),		# set of enabled transitions for Gm
				('r2','r1','w'),
				('r2','r3','s'),
				('r3','r2','n'),
				('r3','r7','e'),
				('r7','r3','w'),
				('r3','r4','s'),
				('r4','r3','n'),
				('r4','r5','s'),
				('r5','r4','n'),
				('r6','r5','e'),
				('r5','r6','w')]
x0_Gm = 'r1'					# initial state for Gm
Gm = G(E_Gm, X_Gm, T_Gm, x0_Gm)

Gn = getParallelComposition(Gr,Gm)
#includes blocked moves
print("The parallel composition of Gr and Gm")
Gn.printG()



# q4
print("\n\n\nQ4")

E_partialObs = ['n','e','s','w']	# set of partially observable states
partialObsGn = Gn
partialObsGn.makeEventsPartiallyObservable(E_partialObs,'m')

print("The parallel composition of Gr and Gm with movement made partially observable")
partialObsGn.printG()

# q5
print("\n\n\nQ5 part 1")
x0_obsGn = [1] * len(partialObsGn.X)
obsGn = getObserverG(partialObsGn,x0_obsGn)
print("The observer automaton for the partially observable automaton in Q4 has", len(obsGn.X), "states")

print("\nQ5 part 2")
print("The states of the observer automaton are:")
printList(obsGn.X)
print("The row sum is:")
print(obsGn.getXRowSum())
print("The column sum is:")
print(obsGn.getXColSum())
print("The first 4 singular values are: ")
print(obsGn.getXSingVals()[0:4])
# obsGn.printG()

# still need to list row sum and column sum and the singular value whatever that is
print("\nQ5 part 3")


print("\nQ5 part 4")
event_sequence = ['m','r','r','m','r','m','r','r','m','r','m']
final_x = obsGn.traverseG(event_sequence, x0_obsGn)
if final_x != None:
	print("The following sequence of events is applied:")
	print(event_sequence)
	print("The final state was:")
	print(final_x)
	final_x_name = []
	for idx, x in enumerate(partialObsGn.X):	
		if final_x[idx] == 1:
			final_x_name.append(x)
	print("This corresponds to state: ", final_x_name)
print("The observer automaton can be used to find the position of the ending state by traversing it according to its transition matrix")
print("Each state is a vector of 1s or 0s where each element of the vector corresponds to a particular state in Gn. The final state reached in the observer automaton only has a single 1. This means that there is only one possible state that the automaton could have ended up in.")
print("The final state is the state that corresponds to the set element of the state vector.")

# Q6

print("\n\n\nQ6")

print("From Gm we can tell that as long as the sequence of events allows the robot to traverse at least 4 different rooms then the robot will always be able to tell where it ends up as there are no sets of 4 connected rooms that are rotationally symmetrical")
print("In other words, all possible paths that have 4 or more different connected rooms will uniquely identify the robots position (but not heading)")
print("Once the position is identified, the heading can be found by looking at the transitions between different states given that the robot can only move in the direction that it is facing.")

print("\nThe observer automaton for the partially observed Gn shows this more clearly as there are sequences where both the robot's position and heading will be certain.")
print("The fact that some of the elements of the row sum of the state matrix are 1s tells us that the some of the states in the observer automaton have only one possible state in Gn")
# create new automaton Gy for room layout

s_events = ['n','e','s','w']
s_states = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6']
s_transitions = [('r1','r2','e'),
				('r2','r1','w'),
				('r2','r3','s'),
				('r3','r2','n'),
				('r3','r4','s'),
				('r4','r3','n'),
				('r4','r5','s'),
				('r5','r4','n'),
				('r6','r5','w'),
				('r5','r6','e')]
x0_Gy = 'r1'
Gy = G(s_events, s_states, s_transitions, x0_Gy)
Gr_Gy = getParallelComposition(Gr,Gy)

E_partialObsGr_Gy = ['n','e','s','w']
partialObsGr_Gy = Gr_Gy
partialObsGr_Gy.makeEventsPartiallyObservable(E_partialObsGr_Gy,'m')

# Get observer automaton
x0_obsGr_Gy = [1] * len(partialObsGr_Gy.X)
obsGr_Gy = getObserverG(partialObsGr_Gy, x0_obsGr_Gy)
final_x_Gr_Gy = obsGr_Gy.traverseG(event_sequence, x0_obsGr_Gy)
print(final_x_Gr_Gy)

print("Let's refer to the automaton in figure 2 as Gy and the parallel composition of Gr and Gy as Gry")

print("Firstly, the route created by following the sequence of events given in question 3 is not possible in Gry.")
print("This can be visually verified by looking at the shape of the path that is created from following such a sequence and seeing that there is no possible starting point in Gry that allows that path.")
print("\nIn the general case, the robot will never be able to have certainty in its position and heading if the room layout is Gy as the automaton is rotationally symmetrical and also there is no state that maintains its position within Gy after being rotated 180 degrees (such a state can be created if there was a room between rm3 and rm4)")
print("This can be verified by looking at the row sum of the state space of the observer automaton generated from the partially observed Gry")
print("None of the elements of the row sum are 1, this indicates that there are no sequences of events in Gry that that lead to a unique final position and heading")

print("The states of the observer automaton for Gry are:")
printList(obsGr_Gy.X)
print("The row sum is:")
print(obsGr_Gy.getXRowSum())
print("The column sum is:")
print(obsGr_Gy.getXColSum())
print("The first 4 singular values are: ")
print(obsGr_Gy.getXSingVals()[0:4])	