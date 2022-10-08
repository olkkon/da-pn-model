
import threading
import copy
from abc import ABC, abstractmethod

# abstract base class for states. Caller will initialize internal variables and thus
# takes care of them - they can be omitted here
class State:
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        
def statesEqual(state1, state2):
    return state1.name == state2.name
    
def stateInStoppingStates(state, stoppingStates):
    for stopState in stoppingStates:
        if statesEqual(state, stopState):
            return True
    return False
    
#############################################

SIMULATION_SPEED = 1.0
DEBUG_ROUND_COUNT = 5

def addOrAppend(dic, key, value):
    if key in dic.keys():
        dic[key].append( value )
    else:
        dic[key] = [ value ]

# abstract base class for distributed algorithms
class DistributedAlgorithm(ABC):

    # a special flag to announce that message will be sent to all ports
    ALLPORTS = 100100

    # input is the set of local inputs
    @abstractmethod
    def input(self):
        pass
        
    # states is the set of states
    @abstractmethod
    def states(self):
        pass
        
    # output <_ states is the set of stopping states (local outputs)
    @abstractmethod
    def output(self):
        pass
        
    # msg is the set of possible messages
    @abstractmethod
    def msg(self):
        pass

    # init: input -> states initializes the state machine
    @abstractmethod
    def init(self, input_, d):
        pass

    # send: states -> msg constructs outgoing messages
    @abstractmethod
    def send(self, state, d):
        pass
        
    # receive: states x msg -> states processes incoming messages
    @abstractmethod
    def receive(self, state, messages, d):
        pass
        
    # by the way, messages msg are tuples (MSG, port)
        
    ############# driver functions #############
    def run(self):         
        try:
            algo_input = self.input()
        except AssertionError:
            print('The input graph does not meet the requirements')
            return
        
        states = {}
        for node in self.graph.nodes:
            states[node] = self.init(node.color, node.degree())
         
        def allNodesInStoppingState():
            stoppingStates = self.output()
            for state in states.values():
                if not stateInStoppingStates(state, stoppingStates):
                    return False
                    
            return True
                
        # runs one round of the distributed algorithm
        def simulate():        
            if allNodesInStoppingState() or (self.counter >= DEBUG_ROUND_COUNT):
                return states
                
            # send messages
            messages = {}
            for node in self.graph.nodes:
                msg = self.send(states[node], node.degree()) 
                if msg != ():
                    # messages = dictionary: receiver node -> list[(msg, target port)]
                    port = msg[1]
                    if port == self.ALLPORTS:
                        for edge in node.edges():
                            target = edge.getAdjacentNode(node)
                            addOrAppend(messages, target, (msg[0], edge.portNumberForNode(target) ) )
                    else:
                        (targetNode, targetPort) = node.getAdjacentByPortNumber(port)
                        addOrAppend(messages, targetNode, (msg[0], targetPort) )
                    
            # receive messages and change state
            for node in self.graph.nodes:
                if node in messages.keys():
                    V = messages[node]
                else:
                    V = []
                    
                states[node] = self.receive(states[node], V, node.degree())
        
            threading.Timer(SIMULATION_SPEED, simulate).start()
            self.counter += 1
            
        # start the algorithm
        simulate()
        
    def __init__(self, desc, graph):
        self.graph = graph
        self.desc = desc
        self.counter = 0
        
    def reset(self):
        self.counter = 0
        
        
# message encodings
PROPOSAL = 1
ACCEPT = 2
MATCHED = 3
        
class BipartiteMaximalMatching(DistributedAlgorithm):

    # we assume proper 2-coloring so the input will consist of two different integers
    def input(self):
        colors = self.graph.colorsInGraph()
        assert(len(colors) == 2)
        return list(colors)
        
    def states(self):
        return [self.WUR, self.BUR, self.MR, self.US, self.MS]
        
    def output(self):
        return [self.US, self.MS]
        
    def msg(self):
        return [PROPOSAL, ACCEPT, MATCHED]

    def init(self, input_, d):
        if input_ == min(self.input()):
            return copy.copy(self.WUR)
        else:
            result = copy.copy(self.BUR)
            result.X = set([i for i in range(1, d + 1)])
            return result
            
    def send(self, state, d):
        if statesEqual(state, self.WUR):
            k_even = (state.k % 2 == 0)
            if k_even:
                return ()
            elif (not k_even) and (state.k <= d):
                return (PROPOSAL, int((state.k + 1) / 2))
            elif (not k_even) and (state.k > d):
                return ()
        elif statesEqual(state, self.BUR):
            if (state.k % 2 == 0) and (len(state.M) > 0):
                return (ACCEPT, min(state.M))
            else:
                return ()
        elif statesEqual(state, self.MR):
            if (state.k % 2 != 0):
                return (MATCHED, self.ALLPORTS)
            else:
                return ()
        elif statesEqual(state, self.US):
            return ()
        elif statesEqual(state, self.MS):
            return ()
        
    def receive(self, state, messages, d):
        if statesEqual(state, self.WUR):
            acceptMessage = next((x for x in messages if x[0] == ACCEPT), None)
            if (state.k % 2 != 0) and (state.k > d):
                return copy.copy(self.US)
            elif (acceptMessage != None):
                result = copy.copy(self.MR)
                result.i = acceptMessage[1]
                return result
            else:
                state.k += 1
                return state
        elif statesEqual(state, self.BUR):
            k_even = (state.k % 2 == 0)
            if not k_even:
                proposals_messages = list(filter(lambda x: x[0] == PROPOSAL, messages))
                proposals = set(map(lambda x: x[1], proposals_messages))
                accepts_messages = list(filter(lambda x: x[0] == ACCEPT, messages))
                accepts = set(map(lambda x: x[1], accepts_messages))
                
                state.k += 1
                state.M.update(proposals)
                state.X = state.X - accepts
                return state
            elif k_even and (len(state.M) > 0):
                result = copy.copy(self.MS)
                result.i = min(state.M)
                return result
            elif k_even and (len(state.X) == 0):
                return copy.copy(self.US)
            else:
                state.k += 1
                return state
        elif statesEqual(state, self.MR):
            if (state.k % 2 != 0):
                result = copy.copy(self.MS)
                result.i = state.i
                return result
            else:
                state.k += 1
                return state
        elif statesEqual(state, self.US):
            return state
        elif statesEqual(state, self.MS):
            return state
        
    def __init__(self, desc, graph):
        DistributedAlgorithm.__init__(self, desc, graph)
         
        # define the states for the problem
        self.WUR = State('WUR', 'White unmatched running')
        self.WUR.k = 1
        
        self.BUR = State('BUR', 'Black unmatched running')
        self.BUR.k = 1
        self.BUR.M = set()
        self.BUR.X = set() # caller needs to init this, as it's degree dependent
        
        self.MR = State('MR', 'Matched running')
        self.MR.k = 1
        self.MR.i = -1
        
        self.US = State('US', 'Unmatched stopped')

        self.MS = State('MS', 'Matched stopped')
        self.MS.i = -1
        
    
