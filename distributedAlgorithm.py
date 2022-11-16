
import copy
import math
from abc import ABC, abstractmethod

# a special flag to announce that message will be sent to all ports
ALLPORTS = 100100

# a special flag used in simulation to show as empty message
SIM_EMPTY_MESSAGE = -1

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
        if value in dic[key]:
            raise Exception('duplicate port number for messages detected')
            
        dic[key].append( value )
    else:
        dic[key] = [ value ]

# abstract base class for distributed algorithms
class DistributedAlgorithm(ABC):

    # input is the set of local inputs
    @abstractmethod
    def input(self):
        pass
        
    # validate input (for example: require that it's bipartite)
    # gets input from function above
    @abstractmethod
    def validateInput(self):
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
    def init(self, name, input_, d):
        pass

    # send: states -> msg constructs outgoing messages
    @abstractmethod
    def send(self, nodeName, state, d):
        pass
        
    # receive: states x msg -> states processes incoming messages
    # by the way, messages msg are tuples (MSG, port)
    @abstractmethod
    def receive(self, nodeName, state, messages, d):
        pass
        
    # returns internal variables for the state
    @abstractmethod
    def paramsByState(self, state):
        pass
        
    def virtualNodeByName(self, name, number):
        if not self.virtual:
            raise Exception('Can not query for simulation nodes without simulation!')
            
        return self.virtualNetwork.nodeByName(name + '_' + str(number))
      
    # FOR INTERNAL USE ONLY
    def beforeRun(self):
        if self.allNodesInStoppingState(self.beforeRoundStates):
            print('Running tried even though all nodes are in stopped states!')
            return False
        
        if not self.running:
            if not self.initializeInternalState():
                return False
            else:
                self.running = True
        else:
            self.beforeRoundStates = copyStates(self, self.afterRoundStates)
            
        return True
      
    # normal running mode (without simulation)
    def runOneRound(self):         
          
        if not self.beforeRun():
            return
             
        self.sendAndReceiveMessages()
        self.counter += 1
        
        if self.allNodesInStoppingState(self.afterRoundStates):
            self.running = False
              
    # simulation running mode
    def runOneRoundSimulated(self):
        
        if not self.virtual:
            print('Virtual network- and problem required to run simulations!')
            return
            
        if not self.beforeRun() or not self.virtualProblem.beforeRun():
            return
                
        self.sendAndReceiveMessages()
        
        self.counter += 1
        self.virtualProblem.counter += 1
        
        if self.allNodesInStoppingState(self.afterRoundStates):
            self.running = False 
            
        if self.virtualProblem.allNodesInStoppingState(self.virtualProblem.afterRoundStates):
            self.virtualProblem.running = False 

    # FOR INTERNAL USE ONLY
    def sendAndReceiveMessages(self):
    
        # send messages
        messages = self.mapOutgoingToIncoming(self.constructOutgoingMessages())
                
        # receive messages and change state
        for node in self.graph.nodes:
            if node in messages.keys():
                V = messages[node]
            else:
                V = []
                
            self.setNewStateBasedOnMessages(node, V)
            
         
    # FOR INTERNAL USE ONLY
    def initializeInternalState(self):
        if not self.validateInput():
            print('The input graph does not meet the requirements')
            return False
            
        if self.virtual:
            self.initializeVirtual()
            
        for node in self.graph.nodes:
            self.beforeRoundStates[node] = self.init(node.name, node.color, node.degree())
            
        return True
            
    # FOR INTERNAL USE ONLY
    # dict: sending node -> list[(msg, port)]
    def constructOutgoingMessages(self):
    
        # A little helper functions to reduce the boilerplate below
        def addForAllPorts(messages, node, message, doubleMessage = None, doubleMessagePort = None):
            for edge in node.edges():
                port = edge.portNumberForNode(node)
                
                if port == doubleMessagePort:
                    addOrAppend(messages, node, (doubleMessage, port ) )
                else:
                    addOrAppend(messages, node, (message, port ) )
                    
        def constructMessagesForSingleNode(messages, node, port, msg):
            if port == ALLPORTS:
                addForAllPorts(messages, node, msg)   
            else:
                addOrAppend(messages, node, (msg, port) )
    
        messages = {}
        for node in self.graph.nodes:
            msg = self.send(node.name, self.beforeRoundStates[node], node.degree()) 
            
            # Both V1 or V2 can send one message or message to all ports or no message at all
            # this adds complexity to this part of the code
            
            if self.virtual:              
                v1_sends = (msg[0] != SIM_EMPTY_MESSAGE) and (msg[0] != ())
                v2_sends = (msg[1] != SIM_EMPTY_MESSAGE) and (msg[1] != ())
            
                if v1_sends and v2_sends:
                    port1 = msg[0][1]
                    port2 = msg[1][1]
                    msg1 = msg[0][0]
                    msg2 = msg[1][0]
                    
                    if port1 == ALLPORTS and port2 == ALLPORTS:
                        addForAllPorts(messages, node, (msg1, msg2)) 
                    elif port1 == ALLPORTS:
                        addForAllPorts(messages, node, (msg1, SIM_EMPTY_MESSAGE), (msg1, msg2), port2)          
                    elif port2 == ALLPORTS:
                        addForAllPorts(messages, node, (SIM_EMPTY_MESSAGE, msg2), (msg1, msg2), port1)  
                    else:
                        if port1 == port2:
                            addOrAppend(messages, node, ((msg1, msg2), port1 ) )
                        else:
                            addOrAppend(messages, node, ((msg1, SIM_EMPTY_MESSAGE), port1 ) )
                            addOrAppend(messages, node, ((SIM_EMPTY_MESSAGE, msg2), port2 ) )

                elif v1_sends:
                    constructMessagesForSingleNode(messages, node, msg[0][1], (msg[0][0], SIM_EMPTY_MESSAGE))
                        
                elif v2_sends:
                    constructMessagesForSingleNode(messages, node, msg[1][1], (SIM_EMPTY_MESSAGE, msg[1][0]))
                    
            else:
                if msg != ():
                    constructMessagesForSingleNode(messages, node, msg[1], msg[0])
                    
        return messages
     
    # FOR INTERNAL USE ONLY
    # dict: sending node -> list[(msg, port)] becomes dict: receiving node -> list[(msg, port)]
    def mapOutgoingToIncoming(self, outgoing):
        incoming = {}
        for index, node in enumerate(outgoing.keys()):
            for msg in outgoing[node]:
                (adj, j) = node.getAdjacentByPortNumber(msg[1])
                addOrAppend(incoming, adj, (msg[0], j))
        
        return incoming
        
    # FOR INTERNAL USE ONLY
    def setNewStateBasedOnMessages(self, node, V):
        self.afterRoundStates[node] = self.receive(node.name, self.beforeRoundStates[node], V, node.degree())
        
    # FOR INTERNAL USE ONLY
    def allNodesInStoppingState(self, states):
        if len(states) == 0:
            return False
        
        stoppingStates = self.output()
        for state in states.values():
            if not stateInStoppingStates(state, stoppingStates):
                return False
                
        return True
        
    # to be called always before running simulation, since the underlying graph might
    # have changed..
    @abstractmethod
    def initializeVirtual(self):
        pass
        
    def __init__(self, desc, graph, virtual):
        self.graph = graph
        self.desc = desc
        self.counter = 0
        self.running = False
        self.beforeRoundStates = {}
        self.afterRoundStates = {}
        self.virtual = virtual
        
        if virtual:
            self.initializeVirtual()
        
    def __str__(self):
        return self.desc
           
    def reset(self):
        self.counter = 0
        self.running = False
        self.beforeRoundStates = {}
        self.afterRoundStates = {}
        
        if self.virtual:
            self.virtualProblem.reset()