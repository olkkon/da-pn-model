
import copy
import math
from abc import ABC, abstractmethod

# abstract base class for states. Caller will initialize internal variables
class State:
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        self.params = lambda: []
    
    def __str__(self):
        return self.toString()
        
    def toString(self):
        strpar = self.params()
        strparlen = len(strpar)
        
        # set() -> [] looks better in UI
        strpar = list(map(lambda a: list(a) if isinstance(a, set) else a, strpar))
    
        if strparlen == 0:
            return self.name
        else:
            output = self.name + "("
            for index in range(strparlen - 1):
                output += str(strpar[index]) + ","
                
            output += str(strpar[strparlen - 1]) + ")"
            return output
            
    def copy(self, alg):
        copiedState = copy.copy(self)
        copiedState.params = lambda: alg.paramsByState(copiedState)
        return copiedState
        
    def equalTo(self, otherState):
        return self.name == otherState.name
    
def copyStates(algorithm, states):
    newStates = {}
    
    for node in states.keys():
        newStates[node] = states[node].copy(algorithm)  
    return newStates
    
def stateInStoppingStates(state, stoppingStates):
    for stopState in stoppingStates:
        if state.equalTo(stopState):
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
        
    # returns internal variables for the state
    @abstractmethod
    def paramsByState(self, state):
        pass
        
    ############# driver functions #############
    def runOneRound(self):         
         
        def allNodesInStoppingState(states):
            
            if len(states) == 0:
                return False
            
            stoppingStates = self.output()
            for state in states.values():
                if not stateInStoppingStates(state, stoppingStates):
                    return False
                    
            return True
         
        if allNodesInStoppingState(self.beforeRoundStates):
            print('Running tried even though all nodes are in stopped states!')
            return
         
        if not self.running:
            self.initializeInternalState()
            self.running = True
        else:
            self.beforeRoundStates = copyStates(self, self.afterRoundStates)
            
        # send messages
        messages = {}
        for node in self.graph.nodes:
            msg = self.send(self.beforeRoundStates[node], node.degree()) 
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
                
            self.afterRoundStates[node] = self.receive(self.beforeRoundStates[node], V, node.degree())
    
        self.counter += 1
        
        if allNodesInStoppingState(self.afterRoundStates):
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
        
    def __str__(self):
        return self.desc
           
    def reset(self):
        self.counter = 0
        self.running = False
        self.beforeRoundStates = {}
        self.afterRoundStates = {}