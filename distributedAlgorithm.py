
import copy
from abc import ABC, abstractmethod

# abstract base class for states. Caller will initialize internal variables and thus
# takes care of them - they can be omitted here
class State:
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        self.strparams = lambda: []
    
    def __str__(self):
        return self.toString()
        
    def toString(self):
        strpar = self.strparams()
        strparlen = len(strpar)
    
        if strparlen == 0:
            return self.name
        else:
            output = self.name + "("
            for index in range(strparlen - 1):
                output += str(strpar[index]) + ","
                
            output += str(strpar[strparlen - 1]) + ")"
            return output
        
def copyState(algorithm, state):
    copiedState = copy.copy(state)
    copiedState.strparams = lambda: algorithm.strparamsByState(copiedState)
    return copiedState
        
def statesEqual(state1, state2):
    return state1.name == state2.name
    
def stateInStoppingStates(state, stoppingStates):
    for stopState in stoppingStates:
        if statesEqual(state, stopState):
            return True
    return False
    
#############################################

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
        
    # returns variables to be printed for the state
    @abstractmethod
    def strparamsByState(self, state):
        pass
        
    ############# driver functions #############
    def runOneRound(self):         
         
        def allNodesInStoppingState():
            
            if len(self.beforeRoundStates) == 0:
                return False
            
            stoppingStates = self.output()
            for state in self.beforeRoundStates.values():
                if not stateInStoppingStates(state, stoppingStates):
                    return False
                    
            return True
         
        if allNodesInStoppingState():
            print('Running tried even though all nodes are in stopped states!')
            return
         
        if not self.running:
            self.initializeInternalState()
            self.running = True
            internalStates = self.beforeRoundStates
        else:
            internalStates = self.afterRoundStates
            
        # send messages
        messages = {}
        for node in self.graph.nodes:
            msg = self.send(internalStates[node], node.degree()) 
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
                
            self.afterRoundStates[node] = self.receive(internalStates[node], V, node.degree())
    
        self.counter += 1
        
        if allNodesInStoppingState():
            self.running = False
         
    def initializeInternalState(self):
        try:
            algo_input = self.input()
        except AssertionError:
            print('The input graph does not meet the requirements')
                        
        for node in self.graph.nodes:
            self.beforeRoundStates[node] = self.init(node.color, node.degree())
        
    def __init__(self, desc, graph):
        self.graph = graph
        self.desc = desc
        self.counter = 0
        self.running = False
        self.beforeRoundStates = {}
        self.afterRoundStates = {}
           
    def reset(self):
        self.counter = 0
        self.running = False
        self.beforeRoundStates = {}
        self.afterRoundStates = {}
        
        
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
            return copyState(self, self.WUR)
        else:
            result = copyState(self, self.BUR)
            result.M = set()
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
                return copyState(self, self.US)
            elif (acceptMessage != None):
                result = copyState(self, self.MR)
                result.k = state.k + 1
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
                matched_messages = list(filter(lambda x: x[0] == MATCHED, messages))
                matched = set(map(lambda x: x[1], matched_messages))
                
                state.k += 1
                state.M.update(proposals)
                state.X = state.X - matched
                return state
            elif k_even and (len(state.M) > 0):
                result = copyState(self, self.MS)
                result.i = min(state.M)
                return result
            elif k_even and (len(state.X) == 0):
                return copyState(self, self.US)
            else:
                state.k += 1
                return state
        elif statesEqual(state, self.MR):
            if (state.k % 2 != 0):
                result = copyState(self, self.MS)
                result.i = state.i
                return result
            else:
                state.k += 1
                return state
        elif statesEqual(state, self.US):
            return state
        elif statesEqual(state, self.MS):
            return state
            
    def strparamsByState(self, state):
        if statesEqual(state, self.WUR):
            return [state.k]
        elif statesEqual(state, self.BUR):
            return [state.k, list(state.M), list(state.X)]
        elif statesEqual(state, self.MR):
            return [state.k, state.i]
        elif statesEqual(state, self.US):
            return []
        elif statesEqual(state, self.MS):
            return [state.i]
        
    def __init__(self, graph):
    
        # define the states for the problem
        self.WUR = State('WUR', 'White unmatched running')
        self.WUR.k = 0
        self.WUR.strparams = lambda: self.strparamsByState(self.WUR)
        
        self.BUR = State('BUR', 'Black unmatched running')
        self.BUR.k = 0
        self.BUR.M = set()
        self.BUR.X = set()
        self.BUR.strparams = lambda: self.strparamsByState(self.BUR)
        
        self.MR = State('MR', 'Matched running')
        self.MR.k = 0
        self.MR.i = -1
        self.MR.strparams = lambda: self.strparamsByState(self.MR)
        
        self.US = State('US', 'Unmatched stopped')

        self.MS = State('MS', 'Matched stopped')
        self.MS.i = -1
        self.MS.strparams = lambda: self.strparamsByState(self.MS)
    
        DistributedAlgorithm.__init__(self, "Bipartite Maximal Matching", graph)
        
